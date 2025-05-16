# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import re


class ChatterWizard(models.TransientModel):
    _name = 'wizard.whatsapp.base.message'
    _description = 'Send template messages to multiple contacts'

    template = fields.Many2one('odx.whatsapp.template', string='Template')
    text_message = fields.Text('Message')
    message = fields.Text('Preview')
    has_params = fields.Boolean(string='Has Parameter', default=False)
    html_preview = fields.Html('Preview', compute="compute_reply_message_preview")
    template_id = fields.Char('Template Id')
    template_name = fields.Char('Template name')
    template_body = fields.Char('Template body')
    header_type = fields.Char('Template header type')
    partner_ids = fields.Many2many('res.partner')
    model = fields.Char('model', readonly='true')
    header_select = fields.Selection([('image', 'Image'),
                                      ('document', 'Document'),
                                      ('video', 'Video'),
                                      ('text', 'Text')], tracking=True,
                                     related='template.header_selector')

    attachment = fields.Binary(string='Attachments')
    attachment_name = fields.Char('Add Attachment Name')
    parameter_ids = fields.One2many('wizard.base.message.paramline', 'whatsapp_template_id', string='Parameter ID')
    line_sequence = fields.Char('Line Sequence')
    media_id = fields.Char('Media Id')
    header_param = fields.Char('Header Params')
    header_has_params = fields.Boolean(string='Header Has Parameter', default=False)
    header_text = fields.Text('Header text')
    session_started = fields.Boolean(string='Session Expired', default=False)
    text_box = fields.Char('Text Message')
    message_mode = fields.Selection([('template', 'Template'),
                                     ('session', 'Session')], default='template')
    session_preview = fields.Html('Session Preview', compute="compute_session_preview")
    model_name = fields.Char(string="Model name")

    @api.onchange('message_mode')
    def onchange_message_mode(self):
        if self.message_mode == 'session':
            self.template = False
        else:
            self.text_box = False

    @api.depends('template')
    def compute_reply_message_preview(self):
        if self.template:
            self.html_preview = self.template.reply_message_preview()
        else:
            self.html_preview = False

    @api.onchange('template')
    def onchange_template_body(self):
        self.header_has_params = False
        self.has_params = False
        self.header_param = False
        if self.template:
            self.message = self.template.template_body
            self.template_id = self.template.m_template_id
            self.template_name = self.template.name
            self.template_body = self.template.template_body
            self.header_type = self.template.header_selector
            if self.header_type == 'text':
                self.header_text = self.template.header_text
                head_has_parameter = str((self.header_text)).count('{{1}}')
                if head_has_parameter != 0:
                    self.header_has_params = True

            has_parameter = str((self.message)).count('{{1}}')
            if has_parameter != 0:
                self.has_params = True

            params = re.findall(r'\{\{(\d+)\}\}', self.template.template_body)
            formatted_list = ['{{' + str(item) + '}}' for item in params]
            parameter_lines = []
            for param in formatted_list:
                parameter_lines.append((0, 0, {'parameter_no': param}))

            self.write({'parameter_ids': False})
            self.write({'parameter_ids': parameter_lines})

    @api.onchange('parameter_ids')
    def onchange_template_body_parameter(self):
        old_temp = str(self.message)
        if self.parameter_ids:
            for rec in self.parameter_ids:
                obj_params = str(rec.parameter_no)
                if rec.value:
                    old_temp = old_temp.replace(obj_params, rec.value)
            self.message = old_temp

        for rec in self:
            if rec.parameter_ids:
                rec.line_sequence = '1'
                for line in rec.parameter_ids:
                    line.parameter_no = "{{" + str(rec.line_sequence) + "}}"
                    rec.line_sequence = str(int(rec.line_sequence) + 1)
            else:
                rec.line_sequence = '1'

    @api.depends('partner_ids')
    def compute_session_preview(self):
        if self.partner_ids:
            preview_html = ''
            for partner in self.partner_ids:
                if partner.whatsappchat_base and partner.whatsapp_number:
                    preview_html = preview_html + partner.name + ' <i class="fa fa-check text-success ml-1"/> '
                else:
                    preview_html = preview_html + partner.name + ' <i class="fa fa-times text-danger ml-1"/> '

            session_active = '<i style="font-size:10px;" class="fa fa-check text-success ml-1"/></span>' + "<span style='color: #C0C0C0; font-size:12px;'> Indicates that the session has started, and can send session and template messages.</span>"
            session_inactive = ' <i style="font-size:10px;" class="fa fa-times text-danger ml-1"/> ' + "<span style='color: #C0C0C0; font-size:12px;'> Indicates that the session has not started, in this case, only the template message will be send. </span>"
            preview_html += "<br><br><span style='color: #FFA500; font-size:12px;'>Messages will be send only to partners with a whatsApp number.</span><br>" + session_active + "<br>" + session_inactive + ""
            self.session_preview = preview_html

    @api.onchange('partner_ids')
    def onchange_partner(self):
        self.session_preview = False
        session_not_started = not any(partner.whatsappchat_base == False for partner in self.partner_ids)
        self.session_started = session_not_started
        if session_not_started == False:
            self.message_mode = 'template'
        else:
            self.message_mode = 'session'
        self.compute_session_preview()

    def action_send(self):
        """Send message"""
        whatsapp_setting = self.env['odx.whatsapp.configuration'].sudo().search([('active', '=', True)], limit=1)
        cur_temp_name = self.template_name
        cur_temp_body = self.template_body
        header_type = self.header_type
        log_dict = {}
        records = self.env[self.model_name].browse(self.env.context.get('active_ids'))
        subtype_id = self.env['mail.message.subtype'].sudo().search([('name', '=', 'Discussions')], limit=1)
        if self.partner_ids:
            for rec in records:
                for partner in self.partner_ids:
                    partner_phone = partner.whatsapp_number
                    if not partner_phone:
                        continue
                    if self.message_mode == 'session':
                        if self.text_box:
                            log_dict = {
                                'subject': 'Whatsapp Message : Sent',
                                'message_type': 'comment',
                                'author_id': self.env.user.partner_id.id,
                                'partner_id': partner.id,
                                'res_id': int(partner.id) if partner.id else False,
                                'subtype_id': subtype_id.id,
                                'is_whatsapp_message': True,
                                'whatsapp_document_model': self.model_name,
                                'whatsapp_document_id': rec.id,
                                'whatsapp_message_state': 'enqueued',
                                'model': 'res.partner',
                                'body': self.text_box,
                            }

                            if partner.whatsappchat_block:
                                log_dict['whatsapp_message_state'] = 'failed'
                                log_dict['whatsapp_failed_reason'] = 'Contact is blacklisted. Unblock to resume messaging.'
                            partner_logs = self.env['mail.message'].sudo().create(log_dict)
                            partner_msg_id = partner_logs.sentWhatsappTextMessage(partner_phone, self.text_box,
                                                                                  whatsapp_setting.token,
                                                                                  whatsapp_setting.graph_api_instance_id)

                    elif self.message_mode == 'template':
                        if self.template:
                            params = []
                            content_param = self.template.template_body.count('{{')
                            line_param = 0
                            create_attachment = False

                            for rec in self.parameter_ids:
                                if rec.value:
                                    params.append(str(rec.value))
                                line_param = line_param + 1
                            if (line_param != content_param):
                                raise UserError('Please add Parameters Properly')
                            if self.has_params == True:
                                if not params:
                                    raise UserError('Please add Parameters Properly')

                            if self.header_has_params == True and not self.header_param:
                                raise UserError('Please add header Parameters.')

                            if self.attachment:
                                mail_message = self.env['mail.message'].sudo()
                                create_attachment = self.env['ir.attachment'].sudo().create({
                                    'type': 'binary',
                                    'datas': self.attachment,
                                    'name': self.attachment_name,
                                    'store_fname': self.attachment_name,
                                    'res_model': 'res.partner',
                                    'res_id': partner.id,
                                    'public': True
                                })
                                file_type = create_attachment.mimetype
                                file_size = create_attachment.file_size
                                attachment_id = create_attachment.id
                                s_fname = create_attachment.store_fname
                                path = create_attachment._full_path(create_attachment.store_fname)
                                file_url = "/web/content/%s" % attachment_id
                                upload_id = mail_message.GetuploadId(file_type, file_size, whatsapp_setting.token,
                                                                     whatsapp_setting.app_id, self.attachment,
                                                                     whatsapp_setting.graph_api_instance_id, file_url, path,
                                                                     s_fname)
                                self.media_id = upload_id
                            if create_attachment:
                                IrConfig = self.env['ir.config_parameter'].sudo()
                                base_url = IrConfig.get_param('report.url') or IrConfig.get_param('web.base.url')
                                download_url = '/web/content/' + str(create_attachment.id) + '?download=true'
                                down_url = str(base_url) + str(download_url)
                            else:
                                down_url = False

                            preview_msg = self.message

                            log_dict = {
                                'subject': 'WhatsApp Template : Sent',
                                'model': 'res.partner',
                                'author_id': self.env.user.partner_id.id,
                                'message_type': 'comment',
                                'partner_id': partner.id,
                                'res_id': int(partner.id) if partner.id else False,
                                'subtype_id': subtype_id.id,
                                'is_whatsapp_message': True,
                                'whatsapp_document_model': self.model_name,
                                'whatsapp_document_id': rec.id,
                                'whatsapp_template_id': self.template.m_template_id if self.template else False,
                                'body': preview_msg,
                                'whatsapp_attachment_url': down_url,
                                'whatsapp_message_state': 'enqueued',
                                'whatsapp_attachment_name': self.attachment_name,
                                'attachment_ids': create_attachment if self.attachment else [],
                            }
                            if partner.whatsappchat_block:
                                log_dict['whatsapp_message_state'] = 'failed'
                                log_dict['whatsapp_failed_reason'] = 'Contact is blacklisted. Unblock to resume messaging.'

                            partner_log = self.env['mail.message'].sudo().create(log_dict)
                            partner_msg_id = partner_log.sentWhatsappTemplateMessage(params, whatsapp_setting.token,
                                                                                     partner_phone,
                                                                                     whatsapp_setting.graph_api_instance_id,
                                                                                     cur_temp_name,
                                                                                     cur_temp_body, header_type,
                                                                                     self.media_id,
                                                                                     self.attachment_name,
                                                                                     self.header_param)

            if (self.model_name != 'res.partner'):
                records = self.env[self.model_name].browse(self.env.context.get('active_ids'))
                if log_dict:
                    self._create_document_log(records,log_dict)
        else:
            raise UserError('Please select a Recipient.')


    def _create_document_log(self, records, log_dict):
        partner_ids = self.partner_ids.filtered(lambda e: not e.whatsappchat_block and e.whatsapp_number)
        recipents_phone = ' | '.join(str(p.name)+'(+'+str(p.whatsapp_number) for p in partner_ids)
        common_log_dict = log_dict
        for rec in records:
              common_log_dict['model'] = self.model_name
              common_log_dict['res_id'] = rec.id if rec.id else False
              common_log_dict['whatsapp_document_model'] = self.model_name
              common_log_dict['whatsapp_document_id'] = rec.id if rec.id else False
              common_log_dict['record_name'] = rec.name if rec else False
              log_dict['partner_ids'] = partner_ids.ids if partner_ids else False
              log_dict['partner_id'] = False
              log_dict['whatsapp_message_state'] = 'document_log'
              if self.message_mode == 'session':
                  log_dict['body'] = "<b>Sent To:" + str(recipents_phone) + ") <br/></b>" + self.text_box
                  document_log = self.env['mail.message'].sudo().create(common_log_dict)
              else:
                  common_log_dict['body'] = "<b>Sent To: " + str(recipents_phone) + "<br/></b>" + self.message

                  document_log = self.env['mail.message'].sudo().create(common_log_dict)

class WizardParamLines(models.TransientModel):
    _name = 'wizard.base.message.paramline'
    _description = 'Wizard Base message Parameter Line'

    parameter_no = fields.Char(string='Parameter', required=True)
    value = fields.Char(string='Value')
    whatsapp_template_id = fields.Many2one('wizard.whatsapp.base.message', string='Template', index=True,
                                           ondelete='cascade')

    @api.model
    def default_get(self, fields):
        defaults = super(WizardParamLines, self).default_get(fields)
        context = self.env.context
        if 'line_sequence' in context:
            sequence = int(context.get('line_sequence'))
            defaults['parameter_no'] = "{{" + str(sequence) + "}}"

        return defaults
