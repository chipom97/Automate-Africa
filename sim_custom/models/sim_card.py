# models/sim_card.py
from odoo import models, fields

class SimCard(models.Model):
    _name = 'sim.card'
    _description = 'SIM Card'

    name = fields.Char(string='SIM Number', required=True)
    activation_date = fields.Date()
    device_imei = fields.Char()
    device_placement = fields.Char()
    phone_number = fields.Char()
    sim_serial_no = fields.Char()
    remarks = fields.Text()
    device_model = fields.Char()
    vehicle_reg_no = fields.Char()
    network_provider = fields.Char()
    reminder = fields.Text()

    partner_id = fields.Many2one('res.partner', string='Customer')
