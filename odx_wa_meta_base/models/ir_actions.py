# -*- coding: utf-8 -*-
from odoo import fields, models


class ServerActions(models.Model):
    _inherit = 'ir.actions.server'

    wa_id = fields.Char(string="wa Id")
