# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class WhatsappTemplate(models.Model):
    _name = 'odx.whatsapp.template'
    _description = "Whatsapp Template"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(whatsappstring='Name', copy=False)
    state = fields.Selection([('draft', 'Draft'),
                              ('PENDING', 'Submitted'),
                              ('SANDBOX_REQUESTED', 'Sandbox Requested'),
                              ('APPROVED', 'Approved'),
                              ('REJECTED', 'Rejected')],
                             string="Status", default="draft",
                             tracking=True)
    rejected_reason = fields.Char('Rejected Reason')
    number = fields.Char(string='Label', copy=False)
    namespace = fields.Char(string='Namespace', copy=False)
    lang_id = fields.Many2one('res.lang', string='Language')
    header_selector = fields.Selection([('image', 'Image'),
                                        ('document', 'Document'),
                                        ('video', 'Video'),
                                        ('text', 'Text')], tracking=True)
    image = fields.Binary('Image')
    document = fields.Binary('Document')
    video = fields.Binary('Video')
    header_text = fields.Char('Header Text')
    template_body = fields.Text('Content')
    footer_selector = fields.Selection([('enable_footer', 'Enable Footer')], string="Footer", tracking=True)
    footer_body = fields.Char('Footer Text')

    button_selector = fields.Selection(
        [('quick_reply', 'Quick Reply'), ('call_to_action', 'Call-to-Action')],
        string="Buttons", tracking=True)

    call_phone_button_text = fields.Char('Button Text')
    call_phone_number = fields.Char('Phone Number')

    website_button_text = fields.Char('Button Text')
    website_url = fields.Char('URL')

    quick_reply_button_text1 = fields.Char('Button Text 1')
    quick_reply_button_text2 = fields.Char('Button Text 2')
    quick_reply_button_text3 = fields.Char('Button Text 3')
    temp_category = fields.Selection([('MARKETING', 'MARKETING'),
                                      ('UTILITY', 'UTILITY'),
                                      ('AUTHENTICATION', 'AUTHENTICATION')])
    configuration_id = fields.Many2one('odx.whatsapp.configuration', string='Configuration')

    m_template_id = fields.Char('Meta Template Id', copy=False)
    meta = fields.Char(string='Meta')
    status = fields.Char(string='Status')
    template_whatsapp_state = fields.Selection(
        [('APPROVED', 'Approved'),
         ('REJECTED', 'Rejected'),
         ('PENDING', 'Pending')],
        string="Whatsapp Status", tracking=True, help="Status of Meta Template", copy=False)
    line_sequence = fields.Char('Line Sequence')
    text_body = fields.Char('Line Sequence')
    company_id = fields.Many2one(string="Company", comodel_name='res.company', default=lambda self: self.env.company.id)
    model_id = fields.Many2one('ir.model', string="Model",help="This model can access this template")
    wa_action_active = fields.Boolean(string="Model Active", compute="_compute_wa_action_active")

    @api.depends('model_id')
    def _compute_wa_action_active(self):
        model = self.env['odx.whatsapp.configuration.line'].search([('model_id', '=', self.model_id.id)], limit=1)
        if model:
            self.wa_action_active = True
        else:
            self.wa_action_active = False

    def activate_whatsapp_action(self):
        """Activate whatsapp action"""
        whatsapp_setting = self.env['odx.whatsapp.configuration'].sudo().search([('active', '=', True)],
                                                                                limit=1)
        if whatsapp_setting:
            models = []
            for line in whatsapp_setting.line_ids:
                models.append(line.model_id.id)
            if self.model_id:
                if self.model_id.id not in models:
                    vals = {
                        'model_id': self.model_id.id
                    }
                    whatsapp_setting.write({'line_ids': ([(0, 0, vals)])})

                whatsapp_setting_line = whatsapp_setting.line_ids.filtered(lambda r: r.model_id.id == self.model_id.id)
                whatsapp_setting_line.activate_whatsapp_action()

    def name_get(self):
        res = []
        for rec in self:
            if rec.number:
                name = rec.number + "-" + rec.name if rec.name else False
                res.append((rec.id, name))
        return res

    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('odx.whatsapp.template')
        result = super(WhatsappTemplate, self).create(vals)
        return result

    def single_sync(self):
        '''Get current template.'''
        configuration = self.env['odx.whatsapp.configuration'].sudo()
        whatsapp_setting = self.env['odx.whatsapp.configuration'].sudo().search([('active', '=', True)],
                                                                                limit=1)
        status = configuration.SynchronizeOne(self.name, whatsapp_setting.graph_api_business_id, whatsapp_setting.token)

    def open_message_preview(self):
        '''Preview wizard open while cliking message preview button'''
        return {
            'name': ' ',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.message.preview',
            'views': [[False, 'form']],
            'context': {'default_preview': self.reply_message_preview()},
            'target': 'new',
        }

    def reply_message_preview(self):

        if self.button_selector:
            button_div = ''

            if self.quick_reply_button_text1:
                button_div += "<div style='background-color:#ffffff;padding:5px;border:none;border-radius:8px;margin:3px;'><span style='font-size:10px;font-weight:500;color:#31a4f1;'>" + self.quick_reply_button_text1 + "</span></div>"
            if self.quick_reply_button_text2:
                button_div += "<div style='background-color:#ffffff;padding:5px;border:none;border-radius:8px;margin:3px;'><span style='font-size:10px;font-weight:500;color:#31a4f1;'>" + self.quick_reply_button_text2 + "</span></div>"
            if self.quick_reply_button_text3:
                button_div += "<div style='background-color:#ffffff;padding:5px;border:none;border-radius:8px;margin:3px;'><span style='font-size:10px;font-weight:500;color:#31a4f1;'>" + self.quick_reply_button_text3 + "</span></div>"

            if self.header_selector == "document" and self.footer_body:
                render_html = "<div  class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span><img src='odx_wa_meta_base/static/description/pdf_document.png' style=' width: 181px;height: 88px;'/></span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='font-size: 10px;opacity: 0.5;'>" + self.footer_body + "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div><div class='row' style='width:200px;float:right;margin-right:10px;'>" + button_div + "</div></div>"
                return render_html
            elif self.header_selector == "image" and self.footer_body:
                render_html = "<div class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span><img src='odx_wa_meta_base/static/description/image.png' style=' width: 181px;height: 88px;background-color: #dddddd;'/></span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='font-size: 10px;opacity: 0.5;'>" + self.footer_body + "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div><div class='row' style='width:200px;float:right;margin-right:10px;'>" + button_div + "</div></div>"
                return render_html

            elif self.header_selector == "document":
                render_html = "<div class='whatsapp_preview'style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span><img src='odx_wa_meta_base/static/description/pdf_document.png' style=' width: 181px;height: 88px;'/></span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div><div class='row' style='width:200px;float:right;margin-right:10px;'>" + button_div + "</div></div>"
                return render_html
            elif self.header_selector == "image":
                render_html = "<div class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span><img src='odx_wa_meta_base/static/description/image.png' style=' width: 181px;height: 88px;background-color: #dddddd;'/></span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div><div class='row' style='width:200px;float:right;margin-right:10px;'>" + button_div + "</div></div>"
                return render_html
            elif self.header_selector == 'text':
                render_html = "<div class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span style='font-weight:bold;font-size: 11px;'>" + self.header_text + "</span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div><div class='row' style='width:200px;float:right;margin-right:10px;'>" + button_div + "</div></div>"
                return render_html
            else:
                render_html = "<div class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span></div><div class='row' style='width:200px;float:right;margin-right:10px;'>" + button_div + "</div></div>"
                return render_html

        else:
            if self.header_selector == "document" and self.footer_body:
                render_html = "<div  class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span><img src='odx_wa_meta_base/static/description/pdf_document.png' style=' width: 181px;height: 88px;'/></span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='font-size: 10px;opacity: 0.5;'>" + self.footer_body + "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div><div class='row' style='width:200px;float:right;margin-right:10px;'></div></div>"
                return render_html
            elif self.header_selector == "image" and self.footer_body:
                render_html = "<div class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span><img src='odx_wa_meta_base/static/description/image.png' style=' width: 181px;height: 88px;background-color: #dddddd;'/></span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div></div>"
                return render_html

            elif self.header_selector == "text" and self.footer_body:
                render_html = "<div class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span style='font-weight:bold;font-size: 11px;'>" + self.header_text + "</span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='font-size: 10px;opacity: 0.5;'>" + self.footer_body + "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div></div>"
                return render_html

            elif self.header_selector == 'text':
                render_html = "<div class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span style='font-weight:bold;font-size: 11px;'>" + self.header_text + "</span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div><div class='row' style='width:200px;float:right;margin-right:10px;'></div></div>"
                return render_html

            elif self.header_selector == 'document':
                render_html = "<div class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span><img src='odx_wa_meta_base/static/description/pdf_document.png' style=' width: 181px;height: 88px;'/></span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='font-size: 10px;opacity: 0.5;'>" "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div><div class='row' style='width:200px;float:right;margin-right:10px;'></div></div>"

                return render_html

            elif self.header_selector == "image":
                render_html = "<div class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span><img src='odx_wa_meta_base/static/description/image.png' style=' width: 181px;height: 88px;background-color: #dddddd;'/></span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div></div>"
                return render_html

            elif self.header_selector == "video":
                render_html = "<div class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span><img src='odx_wa_meta_base/static/description/video.jpg' style=' width: 181px;height: 88px;background-color: #dddddd;'/></span><br/><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div></div>"
                return render_html

            else:
                render_html = "<div class='whatsapp_preview' style='margin:auto;width:250px;height:400px;margin-left: 97px;'><div style='background-color: #3b816a;height: 35px;color: white;'></div><br/><div style='text-align:left;float:right;margin:auto;border:none;border-radius:10px;padding:8px;width:200px;background-color:#ffffff;margin-right:10px;'><span style='font-size:10px;font-weight:500;'>" + self.template_body + "</span><br/><span style='float: right;font-size: 9px;    opacity: 0.5;'>4:22pm</span></div><div class='row' style='width:200px;float:right;margin-right:10px;'></div></div>"
                return render_html
