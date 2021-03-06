# -*- coding: utf-8 -*-
import time

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, AccessError



class SaleAdvancePaymentInvCustom(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice Customization"

    @api.model
    def _get_advance_payment_method(self):
        if self._count() == 1:
            sale_obj = self.env['sale.order']
            order = sale_obj.browse(self._context.get('active_ids'))[0]
            if all([line.product_id.invoice_policy == 'order' for line in order.order_line]) or order.invoice_count:
                return 'all'
        return 'delivered'

    advance_payment_method = fields.Selection([
        ('delivered', 'Invoiceable lines'),
        ('all', 'Invoiceable lines (deduct down payments)'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)'),
        ('progress_percentage', 'Progress claim (percentage)'),
        ('progress_fixed', 'Progress claim (fixed amount)'),

    ], string='What do you want to invoice?', default=_get_advance_payment_method, required=True)
    progress_amount = fields.Float('Progress Amount', digits=dp.get_precision('Account'),
                                   help="The amount to be invoiced in advance, taxes excluded.")

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            return {'value': {'amount': 0}}
        if self.advance_payment_method == 'progress_percentage':
            return {'value': {'progress_amount': 0}}
        return {}

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']

        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_income_id.id or self.product_id.categ_id.property_account_income_categ_id.id
        if not account_id:
            inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _(
                    'There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (self.product_id.name,))
        if self.advance_payment_method == 'percentage' or self.advance_payment_method == "amount":
            if self.amount <= 0.00:
                raise UserError(_('The value of the down payment amount must be positive.'))
        elif self.advance_payment_method == 'progress_percentage' or self.advance_payment_method == "progress_amount":
            if self.progress_amount <= 0.00:
                raise UserError(_('The value of the progress claim amount must be positive.'))

        context = {'lang': order.partner_id.lang}

        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        elif self.advance_payment_method == 'fixed':
            amount = self.amount
            name = _('Down Payment')

        elif self.advance_payment_method == 'progress_percentage':
            amount = order.amount_untaxed * self.progress_amount / 100
            name = _("Progress claim payment of %s%%") % (self.progress_amount,)
        else:
            amount = self.progress_amount
            name = _('Progress claim')

        del context
        taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes).ids
        else:
            tax_ids = taxes.ids

        invoice = inv_obj.create({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
                'account_analytic_id': order.analytic_account_id.id or False,
            })],
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
            'user_id': order.user_id.id,
            'comment': order.note,
        })
        invoice.compute_taxes()
        invoice.message_post_with_view('mail.message_origin_link',
                                       values={'self': invoice, 'origin': order},
                                       subtype_id=self.env.ref('mail.mt_note').id)
        return invoice

    @api.multi
    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            sale_orders.action_invoice_create()
        elif self.advance_payment_method == 'all':
            sale_orders.action_invoice_create(final=True)
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            if self.advance_payment_method == 'progress_percentage' or self.advance_payment_method == "progress_fixed":
                vals = self._prepare_deposit_product_progress()
                self.product_id = self.env["product.product"].search([("name", "=", vals["name"])])
                if not self.product_id:
                    self.product_id = self.env['product.product'].create(vals)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                elif self.advance_payment_method == 'fixed':
                    amount = self.amount

                elif self.advance_payment_method == 'progress_percentage':
                    amount = order.amount_untaxed * self.progress_amount / 100
                else:
                    amount = self.progress_amount

                if self.product_id.invoice_policy != 'order':
                    raise UserError(_(
                        'The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_(
                        "The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(
                    lambda r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                else:
                    tax_ids = taxes.ids
                context = {'lang': order.partner_id.lang}
                so_line = sale_line_obj.create({
                    'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'tax_id': [(6, 0, tax_ids)],
                    'is_downpayment': True,
                })
                del context
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _prepare_deposit_product_progress(self):
        return {
            'name': 'Progress claim',
            'type': 'service',
            'invoice_policy': 'order',
            'property_account_income_id': self.deposit_account_id.id,
            'taxes_id': [(6, 0, self.deposit_taxes_id.ids)],
            'company_id': False,
        }


class JobSelection(models.TransientModel):
    """

    """
    _name = "job.selection"
    existing_job = fields.Many2one('jobs.dashboard')
    job_selection = fields.Selection([
        ('new', 'New Job'),
        ('existing', 'Select from Existing Jobs'),
    ], string='Job Selection', required=True)

    @api.multi
    def create_job(self):
        sale_order = self.env['sale.order'].browse(self._context.get('active_ids', []))
        if sale_order.job_dashboard_id:
            raise ValidationError(_('Error! You cannot select recursive sale orders.'))
        if self.job_selection == "existing":
            self.existing_job.sale_orders = ([sale_order.id])
        else:
            obj = self.env['jobs.dashboard'].create({
                'name': "code",
            })
            sale_order.is_job = True
            obj.sale_orders = ([sale_order.id])

            obj.customer_id = sale_order.partner_id
            obj.delivery_address = sale_order.partner_id.contact_address
            obj.confirmation_date = sale_order.confirmation_date
            obj.currency_id = sale_order.currency_id
            # obj.contract_value = sale_order.amount_total

            return {
                'name': ('Job Dashboard'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'jobs.dashboard',
                'res_id': obj.id,
                'type': 'ir.actions.act_window',
                # 'target': 'new'
            }
