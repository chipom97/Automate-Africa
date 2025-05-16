# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    whatsapp_number = fields.Char(string="WhatsApp Number")
    whatsappchat_base = fields.Boolean(string="Session Started", default=False, compute='create_date_time_stamp')
    whatsappchat_block = fields.Boolean(string="Blacklist", default=False)
    session_expire = fields.Datetime(string="Session Expiring", compute='expiring_date_time')
    time_stamp = fields.Datetime(string="Time stamp")

    def check_user_groups(self):
        user = self.env.user
        domain_list = []
        if user.has_group('odx_wa_meta_base.admin'):
            domain_list = []
        elif user.has_group('odx_wa_meta_base.users'):
            domain_list = []
        else:
            domain_list = [('id', '=', False)]

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'name': 'Contacts',
            'view_mode': 'tree,kanban,form',
            'target': 'current',
            'domain': domain_list,
        }

    def open_whatsapp_base_wizard(self):
        if self.whatsapp_number:
            return {
                'name': 'Send Message',
                'type': 'ir.actions.act_window',
                'res_model': 'wizard.whatsapp.base.message',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_partner_ids': self.ids, 'default_model_name': self._name}
            }
        else:
            raise UserError("No whatsapp number found for the user")

    def open_whatsapp_base_messages(self):
        return {
            'name': 'Send Message',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.whatsapp.base.message',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_ids': self.ids, 'default_model_name': self._name}
        }

    def create_date_time_stamp(self):
        for rec in self:
            rec.whatsappchat_base = False
            if rec.time_stamp:
                now = datetime.now()
                diff = now - rec.time_stamp
                minutes_diff = int(diff.total_seconds() / 60)
                if minutes_diff > 1439:
                    rec.whatsappchat_base = False
                else:
                    rec.whatsappchat_base = True

    @api.onchange('mobile')
    def onchange_mobile(self):
        if self.mobile:
            country_code = self.country_id.phone_code
            mobile_number = self.mobile

            if mobile_number.startswith("+"):
                without_plus = mobile_number.replace("+", "")
                without_spaces = without_plus.replace(" ", "")
                self.whatsapp_number = without_spaces

    def expiring_date_time(self):
        for rec in self:
            start_date = rec.time_stamp

            if start_date:
                start_date = fields.Datetime.from_string(start_date)
                expiration_date = start_date + timedelta(hours=24)
                rec.session_expire = expiration_date.strftime("%Y-%m-%d %H:%M:%S")  # Format as needed
            else:
                rec.session_expire = False
