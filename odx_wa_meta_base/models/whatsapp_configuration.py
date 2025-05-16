# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import requests
import json
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import secrets
import string
import random
import string

DEFAULT_ENDPOINT = "https://graph.facebook.com/v17.0"


class WhatsappConfiguration(models.Model):
    _name = 'odx.whatsapp.configuration'
    _description = 'Account Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def generate_password(self, lenght=30):
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for _ in range(lenght))
        return password

    def default_webhook_url(self):
        IrConfig = request.env['ir.config_parameter'].sudo()
        base_url = IrConfig.get_param('report.url') or IrConfig.get_param('web.base.url')
        hook_url = '/whatsapp/webhook'
        webhook_url = str(base_url) + str(hook_url)
        return webhook_url

    active = fields.Boolean(default=True)
    name = fields.Char(string='App Name')
    graph_api_instance_id = fields.Char(String="Phone Number ID ")
    graph_api_business_id = fields.Char(String="Business Account ID")
    app_id = fields.Char(string='App ID')
    app_name = fields.Char(string='App Name')
    token = fields.Char(string='App Token ')
    api_url = fields.Char('API Url')
    api_version = fields.Char('API Version')
    api_key = fields.Char('Api Key')
    app_secret = fields.Char('App Secret')
    phone_number = fields.Char('Phone Number')
    company_ids = fields.Many2many(string="Company", comodel_name='res.company',
                                   default=lambda self: self.env.company.ids)
    webhook_url = fields.Char('Webhook URL', default=default_webhook_url)
    webhook_token = fields.Char('Webhook Verify Token', default=generate_password)
    authenticate = fields.Boolean('Authenticate')
    test_connection_warning = fields.Text("Warning")
    last_sync_time = fields.Datetime("Last Sync Time")

    line_ids = fields.One2many('odx.whatsapp.configuration.line', 'configuration_id', string="Configuration Line")
    attachment_create = fields.Boolean(string="Attachment",
                                       default=True)

    @api.constrains('active')
    def _check_unique_active(self):
        multiple_active_records = self.env['odx.whatsapp.configuration'].search_count([('active', '=', True)])
        if multiple_active_records > 1:
            raise ValidationError("Only one record can have active set to True.")

    def open_whatsapp_wizard(self, model, records):
        """Open whatsapp wizard"""
        if model._name == 'res.partner':
            partner_ids = []
            for rec in records:
                partner_ids.append(rec.id)
            return {
                'name': 'Send Message',
                'type': 'ir.actions.act_window',
                'res_model': 'wizard.whatsapp.base.message',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_partner_ids': partner_ids, 'default_model_name': model._name},
            }
        else:
            partner_ids = []
            for rec in records:
                if hasattr(rec, 'partner_id') and rec.partner_id is not None:
                    if rec.partner_id:
                        partner_ids.append(rec.partner_id.id)
            return {
                'name': 'Send Message',
                'type': 'ir.actions.act_window',
                'res_model': 'wizard.whatsapp.base.message',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_partner_ids': partner_ids, 'default_model_name': model._name}
            }
    def active_button(self):
        self.active = True
    def inactive_button(self):
        self.active = False


    def action_refresh(self):
        """Synchronize"""
        '''Get Template and account details.'''
        test_con = self.test_connection()
        if test_con == True:
            for rec in self:
                token = rec.token
                url = DEFAULT_ENDPOINT + "/%s/message_templates?fields=name,rejected_reason,components,category,language,status&limit=100000" % (
                    rec.graph_api_business_id)

                payload = {}
                headers = {
                    'Authorization': 'Bearer %s' % (token),
                    'Content-Type': 'text/plain'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                response_dict = json.loads(response.text)
                data = response_dict.get('data')
                error = response_dict.get('error')

                whatsapp_templates = []

                if data:
                    for temp in data:

                        code = temp.get('language')
                        language = rec.env['res.lang'].search([('code', '=', code)], limit=1)
                        vals = {
                            'name': temp.get('name'),
                            'state': temp.get('status'),
                            'template_whatsapp_state': temp.get('status'),
                            'rejected_reason': temp.get('rejected_reason'),
                            'temp_category': temp.get('category'),
                            'm_template_id': temp.get('id'),
                            'lang_id': language.id,
                            'configuration_id': rec.id
                        }

                        name = temp.get('name')
                        existing_template = self.env['odx.whatsapp.template'].search([('name', '=', name)])

                        components = temp.get('components', [])

                        for component in components:
                            if component.get('type') == 'BODY':
                                template_body_text = component.get('text')
                                vals['template_body'] = template_body_text

                            if component.get('type') == 'HEADER':
                                if component.get('format') == 'TEXT':
                                    vals['header_selector'] = 'text'
                                    header_text_body = component.get('text')
                                    vals['header_text'] = header_text_body
                                elif component.get('format') == 'IMAGE':
                                    vals['header_selector'] = 'image'
                                elif component.get('format') == 'DOCUMENT':
                                    vals['header_selector'] = 'document'
                                elif component.get('format') == 'VIDEO':
                                    vals['header_selector'] = 'video'
                                else:
                                    pass

                            if component.get('type') == 'FOOTER':
                                vals['footer_selector'] = 'enable_footer'
                                vals['footer_body'] = component.get('text')

                            if component.get('type') == 'BUTTONS':
                                quick_reply_buttons_count = 0
                                quick_reply_texts = []
                                buttons = component.get('buttons')
                                for btn in buttons:
                                    if btn.get('type') == 'QUICK_REPLY':
                                        vals['button_selector'] = "quick_reply"
                                        quick_reply_buttons_count += 1
                                        quick_reply_texts.append(btn.get('text'))

                                        if quick_reply_buttons_count == 1:
                                            vals['quick_reply_button_text1'] = quick_reply_texts[0]
                                        if quick_reply_buttons_count == 2:
                                            vals['quick_reply_button_text1'] = quick_reply_texts[0]
                                            vals['quick_reply_button_text2'] = quick_reply_texts[1]
                                        if quick_reply_buttons_count == 3:
                                            vals['quick_reply_button_text1'] = quick_reply_texts[0]
                                            vals['quick_reply_button_text2'] = quick_reply_texts[1]
                                            vals['quick_reply_button_text3'] = quick_reply_texts[2]

                        if existing_template:
                            existing_template.write(vals)
                        else:
                            whatsapp_templates.append(vals)

                    if whatsapp_templates:
                        self.env['odx.whatsapp.template'].create(whatsapp_templates)

                    self.last_sync_time = datetime.now()

        else:
            self.authenticate = False

    def SynchronizeOne(self, name, business_id, token):
        """Synchronize current account details"""

        url = DEFAULT_ENDPOINT + "/%s/message_templates?name=%s&fields=rejected_reason,name,components,category,status&limit=100000" % (
            business_id, name)
        payload = {}
        headers = {
            'Authorization': 'Bearer %s' % (token),
            'Content-Type': 'text/plain'

        }

        response = requests.request("GET", url, headers=headers, data=payload)
        response_dict = json.loads(response.text)

        data = response_dict.get('data')

        if data:
            for temp in data:

                code = temp.get('language')
                language = self.env['res.lang'].search([('code', '=', code)], limit=1)
                vals = {
                    'name': temp.get('name'),
                    'state': temp.get('status'),
                    'template_whatsapp_state': temp.get('status'),
                    'rejected_reason': temp.get('rejected_reason'),
                    'temp_category': temp.get('category'),
                    'm_template_id': temp.get('id'),
                    'lang_id': language.id,
                    'configuration_id': self.id

                }

                name = temp.get('name')
                existing_template = self.env['odx.whatsapp.template'].search([('name', '=', name)])

                components = temp.get('components', [])

                for component in components:
                    if component.get('type') == 'BODY':
                        template_body_text = component.get('text')
                        vals['template_body'] = template_body_text

                    if component.get('type') == 'HEADER':
                        if component.get('format') == 'TEXT':
                            vals['header_selector'] = 'text'
                            header_text_body = component.get('text')
                            vals['header_text'] = header_text_body
                        elif component.get('format') == 'IMAGE':
                            vals['header_selector'] = 'image'
                        elif component.get('format') == 'DOCUMENT':
                            vals['header_selector'] = 'document'
                        else:
                            pass
                    if component.get('type') == 'BUTTONS':
                        quick_reply_buttons_count = 0
                        quick_reply_texts = []
                        buttons = component.get('buttons')
                        for btn in buttons:
                            if btn.get('type') == 'QUICK_REPLY':
                                vals['button_selector'] = "quick_reply"
                                quick_reply_buttons_count += 1
                                quick_reply_texts.append(btn.get('text'))

                                if quick_reply_buttons_count == 1:
                                    vals['quick_reply_button_text1'] = quick_reply_texts[0]
                                if quick_reply_buttons_count == 2:
                                    vals['quick_reply_button_text1'] = quick_reply_texts[0]
                                    vals['quick_reply_button_text2'] = quick_reply_texts[1]
                                if quick_reply_buttons_count == 3:
                                    vals['quick_reply_button_text1'] = quick_reply_texts[0]
                                    vals['quick_reply_button_text2'] = quick_reply_texts[1]
                                    vals['quick_reply_button_text3'] = quick_reply_texts[2]

                if existing_template:
                    existing_template.write(vals)

    def test_connection(self):
        """Test Connection"""
        self.authenticate = False
        try:
            test_conn = self.button_test_connection()
            if test_conn == True:

                self.authenticate = True
                return True
            else:
                self.authenticate = False
                return False

        except UserError as e:
            raise UserError(str(e))

    def button_test_connection(self):
        """Test Connection"""
        for rec in self:
            account_id = rec.graph_api_business_id
            token = rec.token
            app_id = rec.app_id
            url = DEFAULT_ENDPOINT + "/%s/phone_numbers" % (account_id)
            headers = {
                'Authorization': 'Bearer %s' % (token),

            }
            payload = {}
            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json().get('data', [])
            if data:
                phone_values = [phone['id'] for phone in data if 'id' in phone]
                if rec.graph_api_instance_id not in phone_values:
                    self.test_connection_warning = "Phone Number Id Is Wrong."
                    return False

            else:
                error = response.json().get('error', [])
                self.test_connection_warning = error.get('message')
                return False

            url_upload_session = DEFAULT_ENDPOINT + "/%s/uploads?access_token=%s" % (app_id, token)
            payload1 = {}
            headers1 = {}

            response2 = requests.request("POST", url_upload_session, headers=headers1, data=payload1)

            upload_session_id = response2.json().get('id')

            if not upload_session_id:
                res = response2.json().get('error')
                self.test_connection_warning = res.get('message')
                return False

            return True

    def approved_templates(self):
        """Templates"""
        return {
            'name': 'Templates',
            'type': 'ir.actions.act_window',
            'res_model': 'odx.whatsapp.template',
            'view_type': 'tree',
            'view_mode': 'tree,form',
            'target': 'fullscreen',
        }

    @api.onchange('line_ids')
    def configuration_lines_onchange(self):
        model_data = []
        for line in self.line_ids:
            if line.model_id:
                if line.model_id.name in model_data:
                    raise ValidationError(_('Model %s already selected!') % line.model_id.name)
                model_data.append(line.model_id.name)

    @api.onchange('active')
    def onchange_active(self):
        if self.active == False:
            for line in self.line_ids:
                actions = self.env['ir.actions.server'].sudo().browse(int(line.action_id))
                if actions:
                    actions.unlink_action()







class WhatsappConfigurationLine(models.Model):
    _name = 'odx.whatsapp.configuration.line'
    _description = "Whatsapp configuration line"

    configuration_id = fields.Many2one('odx.whatsapp.configuration', string="Line Id")
    group_ids = fields.Many2many('res.groups', 'group_id', string="Groups",default=lambda self: self.env.ref('odx_wa_meta_base.users'))
    model_id = fields.Many2one('ir.model', string="Model")
    wa_action_active = fields.Boolean(string="Whatsapp action active", compute="_compute_wa_action_active")
    action_id = fields.Char('Action Id')

    @api.depends('model_id', 'configuration_id')
    def _compute_wa_action_active(self):
        for rec in self:
            if rec.model_id:
                actions = self.env['ir.actions.server'].sudo().search(
                    [('model_id', '=', rec.model_id.id), ('wa_id', '=', rec.configuration_id.id),
                     ('binding_model_id', '!=', False)])
                if actions:
                    rec.wa_action_active = True
                else:
                    rec.wa_action_active = False
            else:
                rec.wa_action_active = False

    def activate_whatsapp_action(self):
        """Activate whatsapp action"""
        actions = self.env['ir.actions.server'].sudo().search(
            [('model_id', '=', self.model_id.id), ('wa_id', '=', self.configuration_id.id)])
        if not actions:
            if self.model_id.name:

                if self.model_id.model == 'res.partner':
                    server_action = self.env['ir.actions.server'].create({
                        'name': 'WhatsApp Message ',
                        'code': """action = env['odx.whatsapp.configuration'].sudo().open_whatsapp_wizard(model,records)""",
                        'state': 'code',
                        'model_id': self.model_id.id,
                        'wa_id': self.configuration_id.id,
                        'type': 'ir.actions.server',
                    })
                else:
                    server_action = self.env['ir.actions.server'].create({
                        'name': 'WhatsApp Message ',
                        'code': """action = env['odx.whatsapp.configuration'].sudo().open_whatsapp_wizard(model,records)""",
                        'state': 'code',
                        'model_id': self.model_id.id,
                        'wa_id': self.configuration_id.id,
                        'type': 'ir.actions.server',
                        'binding_view_types': 'form'
                    })

                self.action_id = server_action.id


                server_action.write({
                    'groups_id': [(6, 0, self.group_ids.ids)]
                })

                server_action.create_action()
        else:
            actions.create_action()
            actions.write({
                'groups_id': [(6, 0, self.group_ids.ids)]
            })

    def deactivate_whatsapp_action(self):
        """Deactivate whatsapp action"""
        actions = self.env['ir.actions.server'].sudo().search(
            [('model_id', '=', self.model_id.id), ('wa_id', '=', self.configuration_id.id)])
        if actions:
            actions.unlink_action()

    def update_whatsapp_action(self):
        server_action = self.env['ir.actions.server'].sudo().search(
            [('model_id', '=', self.model_id.id), ('wa_id', '=', self.configuration_id.id)])
        if server_action:
            server_action.write({
                'groups_id': [(6, 0, self.group_ids.ids)]
            })
