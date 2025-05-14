# models/res_partner.py
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    custom_lead_field = fields.Char(string='Custom Lead Field')
    


	