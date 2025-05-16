# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Odoo Meta Base',
    'version': '17.0',
    'author': 'Odox SoftHub LLP',
    'website': "www.odoxsofthub.com",
    'sequence': 1,
    'price': 85,
    "currency": "USD",
    'summary': 'Odoo WhatsApp Integration provides feature to send Session Message,Template messages Multi-Media files to multiple Contacts by using the Meta Graph Api.',
    'description': """Odoo WhatsApp Integration provides feature to send Session Message,Template messages Multi-Media files to multiple Contacts by using the Meta Graph Api.
        Integrating WhatsApp Graph API with Odoo
        Improving communication processes with WhatsApp Odoo integration
        Broadcast WhatsaApp template messages
        Broadcast WhatsaApp  messages
        WhatsApp integration for streamlined business communication in Odoo
        WhatsApp Odoo integration module
        Odoo module for WhatsApp integration
        Efficient communication through WhatsApp API in Odoo
        Odoo module for conveying important messages
        WhatsApp Odoo Meta Base for communication
        Sending template messages in Odoo with WhatsApp
        Sending template messages to Multiple customers
        Sending template messages to Multiple vendors
        Sending template messages to Multiple contacts
        Session messaging features in WhatsApp Odoo Meta Base
        Odoo WhatsApp connector
        WhatsApp integration features in Odoo
        WhatsApp communication in Odoo ERP
        WhatsApp Odoo module template messages
        Setting up WhatsApp in Odoo
        Document sharing features in WhatsApp Odoo integration
        Integrating WhatsApp Cloud API with Odoo
        Integrating WhatsApp Cloud API  Odoo
        WhatsApp template messages for Odoo communication
        Streamlining communication with WhatsApp Odoo Meta 
        Ensuring effective communication with WhatsApp in Odoo Meta 
        Receive messages in Odoo from WhatsApp Meta Base module
        WhatsApp message handling in Odoo Meta Base integration
        Including documents in WhatsApp template messages in Odoo
        WhatsApp Odoo integration for file transmission in template messages
        Attaching documents to template messages in Odoo with WhatsApp
        Connecting WhatsApp Cloud API to Odoo ERP
        Odoo and WhatsApp Cloud API communication integration
        WhatsApp Business API integration for Odoo
        Official WhatsApp API connector for Odoo ERP
        WhatsApp Business official API module for Odoo
        WhatsApp Business API integration for CRM, Sales, Purchase, Accounts
        WhatsApp Integration  for CRM
        WhatsApp Integration  for Project Sales Accounts""",
    'category': 'Extra Tools',
    'support': 'support@odoxsofthub.com',
    'live_test_url': 'https://odoxsofthub.com/whatsapp-integration-odoo/crm-whatsapp-integration-kerala-india',
    'depends': ['contacts'],
    'data': [
        'data/server_action.xml',
        'data/group.xml',
        'security/ir.model.access.csv',
        'views/whatsapp_template_view.xml',
        'views/whatsapp_configuration.xml',
        'views/menu_whatsapp.xml',
        'views/mail_message_view.xml',
        'views/ir_action_view.xml',
        'views/res_partner_view_inherit.xml',
        'wizard/base_message.xml',
        'wizard/preview.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/odx_wa_meta_base/static/css/pdiv.scss',
        ],
    },
    'external_dependencies': {'python': ['phonenumbers']},

    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/whatsapp_gif_image.gif'],
}

