from odoo import api, fields, models, SUPERUSER_ID


class Lead(models.Model):
    _inherit = 'crm.lead'

    prescription_datas = fields.Binary('Prescription', attachment=True)

