# coding: utf-8
from openerp import api
from datetime import date
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import logging
import os

_logger = logging.getLogger(__name__)

class allow_ipaddress(osv.osv):
    _name = 'res.users.allow'
    _description = 'Allow IP to Login odoo'
    
    _columns = {
        'ipaddress': fields.char('IP address', required = True),
        'user_id': fields.many2one('res.users', 'User', ondelete='cascade', required=True, select=True),
    }
    _order = 'ipaddress'
    _defaults = {
        'ipaddress': ''
    }
    _sql_constraints = [
        ('ipaddress_uniq', 'unique (ipaddress,user_id)', 'The ipaddress must be unique !'),
    ]

class res_users(osv.osv):
    _inherit = "res.users"
    _name = "res.users"
    _columns = {
        'allow_lines': fields.one2many('res.users.allow', 'user_id', 'Allow IP'),
        'allow_all': fields.boolean('Allow All', default=True)
    }