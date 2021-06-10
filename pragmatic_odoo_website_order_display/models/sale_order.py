from odoo import api, fields, models, tools, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('progress', 'In Progress'),
        ('ready', 'Ready'),
        ('picked', 'Picked'),
        ('delivered', 'Delivered'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    def action_start(self):
        return self.write({'state': 'progress'})

    def action_complete(self):
        return self.write({'state': 'ready'})