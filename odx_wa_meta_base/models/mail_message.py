# -*- coding: utf-8 -*-
from odoo import fields, models, _
import requests
import json
from odoo.exceptions import UserError
from bs4 import BeautifulSoup

DEFAULT_ENDPOINT = "https://graph.facebook.com/v17.0"


class MailMessage(models.Model):
    _inherit = "mail.message"
    whatsapp_message_id = fields.Char('Message Id')
    whatsapp_template_id = fields.Char('Template Id')
    whatsapp_attachment_url = fields.Char('Attachment URL')
    whatsapp_attachment_name = fields.Char('Attachment Name')
    whatsapp_attachment_type = fields.Char('Attachment Type')
    whatsapp_document_model = fields.Char('Document Model')
    whatsapp_document_id = fields.Char('Document Id')
    whatsapp_failed_reason = fields.Char('Failed Reason')
    is_whatsapp_message = fields.Boolean('Whatsapp Message')
    location = fields.Char('Location')
    partner_id = fields.Many2one("res.partner", string="Partner")

    whatsapp_message_state = fields.Selection(
        selection=[('received', 'Received'),
                   ('document_log','Document Log'),
                   ('enqueued', 'Enqueued'),
                   ('failed', 'Failed'),
                   ('sent', 'Sent'),
                   ('delivered', 'Delivered'),
                   ('read', 'Read')])

    def sentWhatsappTemplateMessage(self, params, token, partner_phone,
                                    phone_number_id, temp_name, template_body,
                                    header_type, mediaId, attachment_name, header_params):
        """Send template messages"""
        partner = self.env['res.partner'].sudo().search([('whatsapp_number', '=', partner_phone)], limit=1)
        if partner and partner.whatsappchat_block:
            return None
        url = DEFAULT_ENDPOINT + "/%s/messages" % (phone_number_id)
        headers = {
            'Authorization': 'Bearer %s' % (token),
            'Content-Type': 'application/json',
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": partner_phone,
            "type": "template",
            "template": {
                "name": temp_name,
                "language": {
                    "code": "en_US"
                },
                "components": [],
            }
        }

        if template_body:
            if params:
                body_parameters = {
                    "type": "body",
                    "parameters": [
                    ]
                }

                for rec in params:
                    params = {
                        "type": "text",
                        "text": "%s" % (rec)
                    }
                    body_parameters["parameters"].append(params)
                payload["template"]["components"].append(body_parameters)

        if header_type:
            header_parameters = {
                "type": "header",
                "parameters": [
                ]
            }
            if header_type == 'document':
                header = {
                    "type": "document",
                    "document": {
                        "id": mediaId,
                        "filename": attachment_name
                    }
                }
                header_parameters["parameters"].append(header)
            elif header_type == 'image':
                header = {
                    "type": "image",
                    "image": {
                        "id": mediaId,
                    }
                }
                header_parameters["parameters"].append(header)
            elif header_type == 'video':
                header = {
                    "type": "video",
                    "video": {
                        "id": mediaId,
                    }
                }
                header_parameters["parameters"].append(header)

            elif header_type == 'text':
                if header_params:
                    header = {
                        "type": "text",
                        "text": header_params,
                    }
                    header_parameters["parameters"].append(header)

            payload["template"]["components"].append(header_parameters)

        datas = json.dumps(payload)

        response = requests.request("POST", url, headers=headers, data=datas)
        response_dict = json.loads(response.text)
        message = response_dict.get('messages')
        error = response_dict.get('error')
        if message:
            msg_id = message[0].get('id')
            self.whatsapp_message_id = msg_id
            return msg_id
        if error:
            error_message = error.get('message')
            raise UserError(error_message)

    def sentWhatsappTextMessage(self, cus_phone, text_message, token, phone_id):
        '''To send text messages.'''
        url = DEFAULT_ENDPOINT + "/%s/messages" % (phone_id)
        partner = self.env['res.partner'].sudo().search([('whatsapp_number', '=', cus_phone)], limit=1)
        if partner and partner.whatsappchat_block:
            return None
        headers = {
            'Authorization': 'Bearer %s' % (token),
            'Content-Type': 'application/json'
        }
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": cus_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text_message
            }
        })

        response = requests.request("POST", url, headers=headers, data=payload)
        response_dict = json.loads(response.text)
        message = response_dict.get('messages')
        error = response_dict.get('error')
        if message:
            msg_id = message[0].get('id')
            self.whatsapp_message_id = msg_id
            return msg_id
        if error:
            error_message = error.get('message')
            raise UserError(error_message)

    def GetuploadId(self, type, size, token, app_id, attachment, phone_id, file, path, fname):
        url = DEFAULT_ENDPOINT + "/%s/media" % (phone_id)

        payload = {
            'type': type,
            'messaging_product': 'whatsapp'
        }

        files = [
            ('file', (
                fname, open(path, 'rb'),
                type))
        ]
        headers = {
            'Authorization': 'Bearer %s' % (token),
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        response_dict2 = json.loads(response.text)

        handle_id = response_dict2.get("id")

        return handle_id

    def sent_message_state(self, message_state):
        self.write({'whatsapp_message_state': message_state})

    def create_records_chatter_other_model(self, text_msg, partner, attachment,location=False,image_caption=False):
        """Create incoming message on chatter"""
        whatsapp_message = self.env['mail.message'].sudo().search(
            [('partner_ids', 'in', [partner.id]),
             ('is_whatsapp_message', '=', True),
             ('whatsapp_message_state', 'not in', ('failed','received')),
             ], order='date desc', limit=1)

        if whatsapp_message:
            if whatsapp_message.whatsapp_document_model != 'res.partner' and whatsapp_message.whatsapp_document_model:
                subtype_id = self.env['mail.message.subtype'].sudo().search([('name', '=', 'Discussions')], limit=1)
                log_dict = {
                    'subject': 'Whatsapp Message: Received',
                    'model': whatsapp_message.whatsapp_document_model,
                    'message_type': 'comment',
                    'res_id': int(
                        whatsapp_message.whatsapp_document_id) if whatsapp_message.whatsapp_document_id else False,
                    'subtype_id': subtype_id.id,
                    'is_whatsapp_message': True,
                    'whatsapp_document_model': whatsapp_message.whatsapp_document_model,
                    'whatsapp_document_id': whatsapp_message.whatsapp_document_id,
                    'whatsapp_message_state': 'received',
                    'author_id': partner.id
                }
                if attachment:
                    if image_caption:
                        log_dict['body'] = image_caption
                    else:
                        log_dict['body'] = attachment.mimetype
                    log_dict['attachment_ids'] = attachment
                    partner_logs = self.env['mail.message'].sudo().create(log_dict)

                elif location:
                    log_dict['body'] = text_msg
                    log_dict["location"] =location
                    partner_logs = self.env['mail.message'].sudo().create(log_dict)

                else:
                    log_dict['body'] = text_msg
                    partner_logs = self.env['mail.message'].sudo().create(log_dict)

                return partner_logs

    def resend_whatsapp_message(self):
        # '''Resend a message by clicking the Resend button.'''
        partner_phone, chatText = False, False
        self.env['res.partner'].browse(self.res_id)
        if self.partner_id:
            partner_phone = self.partner_id.whatsapp_number
        if self.body:
            chatText = BeautifulSoup(self.body, "lxml").text
        whatsapp_setting = self.env['odx.whatsapp.configuration'].sudo().search([], limit=1)
        if self.partner_id.whatsappchat_block:
            self.whatsapp_message_state = 'enqueued'
            self.whatsapp_failed_reason = ''
        if partner_phone and chatText:
            self.sentWhatsappTextMessage(partner_phone, chatText,
                                         whatsapp_setting.token,
                                         whatsapp_setting.graph_api_instance_id)



