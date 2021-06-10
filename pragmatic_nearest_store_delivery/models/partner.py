# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        '''
        method to update geo location of customer
        :param vals:
        :return:
        '''

        res = super(ResPartner, self).create(vals)
        if ('street' in vals) or ('street2' in vals) or ('city' in vals) or ('zip' in vals) or \
                ('state_id' in vals) or ('country_id' in vals):
            res.geo_localize()
        return res

    def write(self, vals):
        '''
        update geo location of customer
        :param vals:
        :return:
        '''

        res = super(ResPartner, self).write(vals)
        for partner in self:
            if ('street' in vals) or ('street2' in vals) or ('city' in vals) or ('zip' in vals) or\
                    ('state_id' in vals) or ('country_id' in vals):
                partner.geo_localize()
        return res

    def get_address_str(self):
        self.ensure_one()
        addrs = []
        if self.street:
            addrs.append(self.street)
        if self.street2:
            addrs.append(self.street2)
        if self.city:
            addrs.append(self.city)
        if self.state_id or self.zip:
            state = ""
            if self.state_id:
                state += self.state_id.name
            if self.zip:
                state += " "+self.zip
            addrs.append(state)
        if self.country_id:
            addrs.append(self.country_id.name)
        return ",".join(addrs)
