# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request
from datetime import datetime
from odoo import SUPERUSER_ID
import logging
import json, requests
import phonenumbers

_logger = logging.getLogger(__name__)


class WebhookController(http.Controller):

    @http.route(['/whatsapp/webhook/'], methods=['POST'], type="json", csrf=False, odx='odx', auth="public")
    def webhookpost(self):
        data = json.loads(request.httprequest.data)
        mail_msg = self.get_mail_message()
        whatsapp_setting = request.env['odx.whatsapp.configuration'].sudo().search([('active', '=', True)],
                                                                                   limit=1)
        for entry in data['entry']:
            for changes in entry.get('changes', []):
                value = changes['value']
                if value.get('statuses'):
                    status = value['statuses']
                    id = status[0]
                    message_id = id.get('id')
                    message_status = id.get('status')
                    if message_id:
                        whatsapp_msg = self.get_mail_message(message_id)
                        whatsapp_msg.sent_message_state(message_status)
                        if message_status == 'failed':
                            failed = status[0]
                            failed_errors = failed.get('errors')
                            for error in failed_errors:
                                whatsapp_msg.whatsapp_failed_reason = error.get('title')

                if value.get('contacts'):
                    contacts = value['contacts']
                    first_contact = contacts[0]
                    profile = first_contact.get('profile', {})
                    name = profile.get('name')
                if value.get('messages'):
                    messages = value['messages']
                    from_messages = messages[0]
                    from_number = from_messages.get('from')
                    message_id = from_messages.get('id')
                    message_type = from_messages.get('type')
                    image = from_messages.get(message_type)
                    image_id = image.get('id')

                    if from_number:
                        number_whatsapp_country = self.get_country_code(from_number)
                        partner = request.env['res.partner'].sudo().search([('whatsapp_number', '=', from_number)],
                                                                           limit=1)
                        subtype_id = request.env['mail.message.subtype'].sudo().search([('name', '=', 'Discussions')])

                        if not partner:
                            if number_whatsapp_country:
                                partner = request.env['res.partner'].sudo().with_user(SUPERUSER_ID).create({
                                    'name': name,
                                    'whatsapp_number': from_number,
                                    'mobile': from_number,
                                    'phone': from_number,
                                    'country_id': number_whatsapp_country,
                                })
                            else:

                                partner = request.env['res.partner'].sudo().with_user(SUPERUSER_ID).create({
                                    'name': name,
                                    'whatsapp_number': from_number,
                                    'mobile': from_number,
                                    'phone': from_number,
                                })

                        if partner.whatsappchat_block:
                            return None

                        if partner.whatsappchat_base == False:
                            now = datetime.now()
                            partner.time_stamp = now

                        log_dict = {
                            'subject': 'Whatsapp Message : Received',
                            'model': 'res.partner',
                            'author_id': partner.id if partner else False,
                            'message_type': 'comment',
                            'res_id': partner.id if partner else False,
                            'subtype_id': subtype_id.id,
                            'is_whatsapp_message': True,
                            'whatsapp_message_id': message_id,
                            'whatsapp_message_state': 'received',
                            'partner_id': partner.id
                        }

                    if message_type == 'text':
                        type_text = from_messages.get('text', {}).get('body')
                        mail_msg.create_records_chatter_other_model(type_text, partner, False)
                        if not partner.whatsappchat_base:
                            now = datetime.now()
                            partner.time_stamp = now
                            partner.whatsappchat_base = True
                            log_dict['body'] = type_text
                            log = self.create_message(log_dict)
                        else:
                            log_dict['body'] = type_text
                            log = self.create_message(log_dict)

                    elif message_type in ('document', 'image', 'audio', 'video'):
                        image_caption = image.get('caption')
                        file_mimetype = image.get('mime_type')
                        file_name = image.get('filename')
                        response = self.media_decoder("GET", f"/{image_id}", auth_type="bearer")
                        response_json = response.json()
                        file_url = response_json.get('url')
                        file_response = self.media_decoder("GET", file_url, auth_type="bearer", endpoint_include=True)
                        datas = file_response.content
                        encoded_data = base64.b64encode(datas)
                        if whatsapp_setting.attachment_create == True:
                            if file_name:
                                attachment = request.env['ir.attachment'].sudo().create({
                                    'type': 'binary',
                                    'datas': encoded_data,
                                    'name': file_name,
                                    'store_fname': file_name,
                                    'res_model': 'res.partner',
                                    'res_id': partner.id,
                                    'mimetype': file_mimetype,
                                })

                            else:
                                attachment = request.env['ir.attachment'].sudo().create({
                                    'type': 'binary',
                                    'datas': encoded_data,
                                    'name': "file",
                                    'store_fname': "filename",
                                    'res_model': 'res.partner',
                                    'res_id': partner.id,
                                    'mimetype': file_mimetype,
                                })
                            mail_msg.create_records_chatter_other_model(attachment.mimetype, partner,
                                                                        attachment,False,image_caption)

                            IrConfig = request.env['ir.config_parameter'].sudo()
                            base_url = IrConfig.get_param('report.url') or IrConfig.get_param('web.base.url')
                            download_url = '/web/content/' + str(attachment.id) + '?download=true'
                            down_url = str(base_url) + str(download_url)
                            if attachment:
                                if image_caption:
                                    log_dict['body'] = image_caption

                                log_dict['whatsapp_attachment_url'] = down_url
                                log_dict['attachment_ids'] = attachment
                                log_dict['whatsapp_attachment_type'] = attachment.mimetype
                                log = self.create_message(log_dict)
                        else:
                            log_dict['body'] = file_url
                            log = self.create_message(log_dict)
                            mail_msg.create_records_chatter_other_model(file_url, partner,
                                                                        False)

                    elif message_type == 'button':
                        text = image.get('payload')
                        mail_msg.create_records_chatter_other_model(text, partner, False)

                        if not partner.whatsappchat_base:
                            now = datetime.now()
                            partner.time_stamp = now
                            partner.whatsappchat_base = True
                            log_dict['body'] = text
                            log = self.create_message(log_dict)
                        else:
                            log_dict['body'] = text
                            log = self.create_message(log_dict)

                    elif message_type == 'location':
                        location = messages[0].get('location')
                        if location:
                            latitude = location.get('latitude')
                            longitude = location.get('longitude')
                            if not partner.whatsappchat_base:
                                now = datetime.now()
                                partner.time_stamp = now
                                partner.whatsappchat_base = True
                                log_dict['body'] = "📍location"
                                log_dict['location'] = {'latitude': latitude, 'longitude': longitude}
                                log = self.create_message(log_dict)
                            else:
                                log_dict['body'] = "📍location"
                                log_dict['location'] = {'latitude': latitude, 'longitude': longitude}
                                log = self.create_message(log_dict)
                            mail_msg.create_records_chatter_other_model("📍location", partner,
                                                                        False, {'latitude': latitude, 'longitude': longitude})

                    if message_type not in ('document', 'image', 'audio', 'video'):
                        attachment = False

    def get_country_code(self, from_number):
        num = "+" + from_number
        try:
            whatsapp_number = phonenumbers.parse(num, None)
            parsed_country_code = str(whatsapp_number.country_code)
            country_record = request.env['res.country'].sudo().search([('phone_code', '=', parsed_country_code)],
                                                                      limit=1)
            return country_record.id
        except:
            return False

    def get_mail_message(self, message_id=None):
        '''Searching messages'''
        if message_id:
            return request.env['mail.message'].sudo().search([('whatsapp_message_id', '=', message_id)])
        else:
            return request.env['mail.message'].sudo()

    def create_message(self, values):
        """Create mail message"""
        return request.env['mail.message'].sudo().create(values)

    def media_decoder(self, request_type, url, auth_type="", params=False, headers=None, data=False, files=False,
                      endpoint_include=False):
        whatsapp_setting = request.env['odx.whatsapp.configuration'].sudo().search([('active', '=', True)],
                                                                                   limit=1)
        headers = headers or {}
        params = params or {}

        token = whatsapp_setting.token

        if auth_type == 'oauth':
            headers.update({'Authorization': f'OAuth {token}'})
        if auth_type == 'bearer':
            headers.update({'Authorization': f'Bearer {token}'})
        call_url = ("https://graph.facebook.com/v17.0" + url) if not endpoint_include else url

        try:
            res = requests.request(request_type, call_url, params=params, headers=headers, data=data, files=files,
                                   timeout=10)
        except requests.exceptions.RequestException:
            pass
        return res

    @http.route(['/whatsapp/webhook/'], methods=['GET'], type="http", auth="public", csrf=False)
    def webhookverify(self, **kw):
        hub_challenge = kw.get('hub.challenge')
        hook_token = kw.get('hub.verify_token')
        if not hub_challenge and hook_token:
            return 400
        if hook_token:
            verify_token = request.env['odx.whatsapp.configuration'].sudo().search([('webhook_token', '=', hook_token)])
            if verify_token:
                pass
            else:
                return 400

        response = request.make_response(hub_challenge)
        return response
