from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    network_issue = fields.Char(string="Network Issue")

    @api.model
    def create(self, vals):
        if isinstance(vals.get('network_issue'), list):
            vals['network_issue'] = ', '.join(vals['network_issue'])
        return super().create(vals)
    
    
    """
    incident_date = fields.Char(string="Date")
    relationship = fields.Char(string="Relationship")
    id_number = fields.Char(string="ID Number")
    description = fields.Text(string="Description of Incident")

    network_issue = fields.Selection([
    ('0_no_signal', 'No signal'),
    ('1_call_drops', 'Call drops'),
    ('2_poor_call_quality', 'Poor call quality'),
], string='Network Issue')

    """