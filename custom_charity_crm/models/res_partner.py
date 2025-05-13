# -*- coding: utf-8 -*-

from odoo import fields, models, _

class ResPartner(models.Model):
	_inherit = 'res.partner'

	customer_type = fields.Selection([
        ('receiver', 'Reciever'),
        ('donor', 'Donor'),
    ], string="Customer Type")

	
