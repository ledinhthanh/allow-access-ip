# coding: utf-8
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.tools.translate import _

class allow_ipaddress(models.Model):
    _name = 'res.users.allow'
    _description = 'Allow IP to Login odoo'
    
    ipaddress = fields.Char('IP address', required = True)
    user_id = fields.Many2one('res.users', 'User', ondelete='cascade', required=True, select=True)

    _order = 'ipaddress'
    _sql_constraints = [
        ('ipaddress_uniq', 'unique (ipaddress,user_id)', 'The ipaddress must be unique !'),
    ]

class res_users(models.Model):
    _inherit = "res.users"
    _name = "res.users"

    allow_lines = fields.One2many('res.users.allow', 'user_id', 'Allow IP')
    allow_all = fields.Boolean('Allow All', default=True)