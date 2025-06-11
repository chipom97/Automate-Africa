# models/res_partner.py
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sim_card_ids = fields.One2many('sim.card', 'partner_id', string='SIM Cards')
    selected_sim_id = fields.Many2one('sim.card', string='Selected SIM')

    # Display-only related fields
    sim_activation_date = fields.Date(related='selected_sim_id.activation_date', readonly=True)
    sim_device_imei = fields.Char(related='selected_sim_id.device_imei', readonly=True)
    sim_device_placement = fields.Char(related='selected_sim_id.device_placement', readonly=True)
    sim_phone_number = fields.Char(related='selected_sim_id.phone_number', readonly=True)
    sim_serial_no = fields.Char(related='selected_sim_id.sim_serial_no', readonly=True)
    sim_remarks = fields.Text(related='selected_sim_id.remarks', readonly=True)
    sim_device_model = fields.Char(related='selected_sim_id.device_model', readonly=True)
    sim_vehicle_reg_no = fields.Char(related='selected_sim_id.vehicle_reg_no', readonly=True)
    sim_network_provider = fields.Char(related='selected_sim_id.network_provider', readonly=True)
    sim_reminder = fields.Text(related='selected_sim_id.reminder', readonly=True)
