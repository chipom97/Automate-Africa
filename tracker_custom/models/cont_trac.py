from odoo import models, fields

class CustomPartner(models.Model):
    _inherit = 'res.partner'
    
    network_issue = fields.Char(string="Network Issue")
    sim_serial_no = fields.Char(string='SIM Serial No.')
    network_provider = fields.Selection(
        selection=[
            ('orange', 'Orange'),
            ('mascom', 'Mascom'),
            ('btc', 'BTC'),
        ],
        string='Network Provider'
    )
    activation_date = fields.Date(string='Activation Date')
    device_model = fields.Char(string='Device Model')
    device_imei = fields.Char(string='Device IMEI')
    vehicle_reg_no = fields.Char(string='Vehicle Reg. No.')
    device_placement = fields.Char(string='Device Placement')
    remarks = fields.Text(string='Remarks')
    reminder = fields.Datetime(string='Reminder')