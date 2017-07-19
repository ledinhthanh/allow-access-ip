from odoo.addons.web.controllers.main import *
from odoo import api, http, SUPERUSER_ID
import threading
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)

class AllowHome(Home):
    
    def logout(self, redirect='/web'):
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)
    # check ip address valid
    def valid_ipaddress(self, _request,login=None):
        registry = odoo.registry(request.session.db)         
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID,{})
            if login != None:
                user = env['res.users'].search([('login','=',login)])
            else:
                user = env['res.users'].browse(request.session.uid)
            if user:
                if user.allow_all != True:
                    allow_env = env['res.users.allow']
                    ips = allow_env.search_read([('user_id','=',user.id)],['ipaddress'])
                    if len(ips):
                        allow_ips = [p["ipaddress"] for p in ips]
                        remote_addr = getattr(threading.currentThread(), 'remote_addr', None)
                        return remote_addr in allow_ips
                    return False
                else:
                    return True
            return True

    @http.route('/', type='http', auth="none")
    def index(self, s_action=None, db=None, **kw):
        return http.local_redirect('/web', query=request.params, keep_hash=True)

    # ideally, this route should be `auth="user"` but that don't work in non-monodb mode.
    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        else:
            ip_valid = self.valid_ipaddress(request)
            if not ip_valid:
                _logger.error("Request from invalid IP address")
                self.logout()
                values = {}
                values = request.params.copy()        
                values['error'] = _("You are not allow access from this IP address")
                return request.render('web.login', values)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        request.uid = request.session.uid
        context = request.env['ir.http'].webclient_rendering_context()

        return request.render('web.webclient_bootstrap', qcontext=context)

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            ip_valid = self.valid_ipaddress(request,request.params['login'])
            if ip_valid:
                old_uid = request.uid
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                if uid is not False:
                    request.params['login_success'] = True
                    if not redirect:
                        redirect = '/web'
                    return http.redirect_with_hash(redirect)
                request.uid = old_uid
                values['error'] = _("Wrong login/password")
            else:
                _logger.error("Request LOGIN from invalid IP address")
                values = {}
                values['error'] = _("You are not allow access from this IP address")
        return request.render('web.login', values)