from openerp.addons.web.controllers.main import *
from openerp import SUPERUSER_ID
import threading
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)

class AllowHome(Home):
    
    def logout(self, redirect='/web'):
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)
    # check ip address valid
    def valid_ipaddress(self, registry, uid, dbname = None):
        if dbname != None:            
            registry = openerp.modules.registry.RegistryManager.get(dbname)
        with registry.cursor() as cr:
            user_env = registry.get('res.users')
            user = user_env.browse(cr,SUPERUSER_ID,uid)
            if user != None:
                if user.allow_all != True:
                    allow_env = registry.get('res.users.allow')
                    ips = allow_env.search_read(cr, SUPERUSER_ID, [('user_id','=',uid)],['ipaddress'])
                    if len(ips):
                        allow_ips = [p["ipaddress"] for p in ips]
                        remote_addr = getattr(threading.currentThread(), 'remote_addr', None)
                        return remote_addr in allow_ips
                    return False
                else:
                    return True
            else:
                return False

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()
        if request.session.uid:
            ip_valid = self.valid_ipaddress(request.registry,request.session.uid)
            if not ip_valid:
                _logger.error("Request from invalid IP address")
                self.logout() 
                values = request.params.copy()        
                error = 'You are not allow access from this IP address'       
                values['error'] = _(error)
                return request.render('web.login', values)
            if kw.get('redirect'):
                return werkzeug.utils.redirect(kw.get('redirect'), 303)
            if not request.uid:
                request.uid = request.session.uid

            menu_data = request.registry['ir.ui.menu'].load_menus(request.cr, request.uid, context=request.context)
            return request.render('web.webclient_bootstrap', qcontext={'menu_data': menu_data})
        else:
            return login_redirect()

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()

        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = SUPERUSER_ID

        values = request.params.copy()
        if not redirect:
            redirect = '/web?' + request.httprequest.query_string
        values['redirect'] = redirect

        try:
            values['databases'] = http.db_list()
        except openerp.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                ip_valid = self.valid_ipaddress(None,uid,request.session.db)
                if ip_valid:
                    return http.redirect_with_hash(redirect)
                else:
                    _logger.error("Request LOGIN from invalid IP address")
                    self.logout()
                    error = 'You are not allow access from this IP address'
                    return werkzeug.utils.redirect('/web/database/selector?error=%s' % error, 303)
            request.uid = old_uid
            values['error'] = _("Wrong login/password")
        if request.env.ref('web.login', False):
            return request.render('web.login', values)
        else:
            # probably not an odoo compatible database
            error = 'Unable to login on database %s' % request.session.db
            return werkzeug.utils.redirect('/web/database/selector?error=%s' % error, 303)

    