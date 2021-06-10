from odoo import models, api
from odoo.exceptions import UserError

class Stock(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def create(self, vals):
        res = super(Stock, self).create(vals)
        if vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            partner.write({'is_warehouse':True})
        return res

    def write(self, vals):
        if vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            partner.write({'is_warehouse': True})
        for rec in self:
            if rec.partner_id:
                warehouse = self.env['stock.warehouse'].search([('partner_id', '=', rec.partner_id.id)]).ids
                if len(warehouse)<=1:
                    partner = self.env['res.partner'].browse(rec.partner_id.id)
                    partner.write({'is_warehouse': False})

        res = super(Stock, self).write(vals)
        return res

    def unlink(self):
        for rec in self:
            if rec.partner_id:
                warehouse = self.env['stock.warehouse'].search([('partner_id', '=', rec.partner_id.id)]).ids
                if len(warehouse) <= 1:
                    partner = self.env['res.partner'].browse(rec.partner_id.id)
                    partner.write({'is_warehouse': False})
                partner = self.env['res.partner'].browse(rec.partner_id.id)
                partner.write({'is_warehouse': False})
        return super(Stock, self).unlink()

class StockWarehouseInherit(models.Model):
    _inherit = "stock.warehouse.driver"

    @api.model
    def create(self, vals):
        if vals.get('driver_id'):
            driver_id = vals.get('driver_id')
            driver_wh = self.env['stock.warehouse.driver'].search([('driver_id', 'in', [driver_id])])
            if driver_wh:
                raise UserError(
                    "You cannot add the delivery boy, the delivery boy is already present in warehouse {}".
                    format(driver_wh.warehouse_id.name))
        res = super(StockWarehouseInherit, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('driver_id'):
            driver_id = vals.get('driver_id')
            driver_wh = self.env['stock.warehouse.driver'].search([('driver_id', 'in', [driver_id])])
            if driver_wh:
                raise UserError(
                    "You cannot add the delivery boy, the delivery boy is already present in warehouse {}".
                        format(driver_wh.warehouse_id.name))
        res = super(StockWarehouseInherit, self).write(vals)
        return res
