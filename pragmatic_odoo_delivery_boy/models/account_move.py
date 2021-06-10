from odoo import fields, models, api, _

class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        # print("\n\nIn write account move******************************",vals,"\nself.id: ",self.id)
        invoice_name = vals.get('name')
        if 'name' in vals and invoice_name.startswith('BNK'):
            if self.invoice_origin:
                # print("\nbefore for self.invoice_origin: ", self.invoice_origin)

                # print("\nself.invoice_origin: ",self.invoice_origin,"\ntype: ",type(self.invoice_origin[2:-2]))
                # sale_ids = self.env['sale.order'].search([])
                # print("invoice_ids: ",sale_ids.invoice_ids)

                # print("\n\ninvoice_origin: ", )
                # sale_id = self.env['sale.order'].browse(self.invoice_origin[2:-2])
                # sale_id = self.env['sale.order'].mapped(self.invoice_origin)
                sale_id = self.env['sale.order'].search([('name', '=', self.invoice_origin[2:-2])])
                # print("\nsale_id: ",sale_id)
                picking_id = self.env['picking.order'].search([('sale_order', '=', sale_id.id)])
                # print("\npicking_id: ",picking_id)
                res_picking = picking_id.write({'invoice': self.id,'payment':'paid'})
                # print("\npicking_id: ",res_picking)
                picking_id_paid_state = picking_id.action_picking_order_paid()
                # print("\npicking_id11: ",picking_id_paid_state)



        return super(AccountMove, self).write(vals)
