# -*- coding: utf-8 -*-

from odoo.modules.module import get_resource_path
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import base64

class crm_portal(models.Model):
	_inherit = 'res.partner'

	location = fields.Char(string="Location")
	city = fields.Char(string="City")
	customer_category = fields.Selection([
        ('type_a', 'Type A'),
        ('type_b', 'Type B'),
    ], string="Customer Category")

	
