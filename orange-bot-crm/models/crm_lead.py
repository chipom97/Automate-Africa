from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    """
    incident_date = fields.Char(string="Date")
    relationship = fields.Char(string="Relationship")
    id_number = fields.Char(string="ID Number")
    description = fields.Text(string="Description of Incident")
    """
    network_issue = fields.Selection([
        ('No signal', 'No signal'),
        ('Call drops', 'Call drops'),
            ('Poor call quality','Poor call quality')
    ], string='Network Issue')