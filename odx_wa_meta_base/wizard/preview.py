# -*- coding: utf-8 -*-
from odoo import fields, models


class WizardPreview(models.TransientModel):
    _name = 'wizard.message.preview'
    _description = 'Whatsapp Message Preview'

    preview = fields.Html(string='preview')
