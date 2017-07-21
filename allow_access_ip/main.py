from openerp.http import WebRequest
import sys
import threading
from openerp import netsvc
import logging

_logger = logging.getLogger(__name__)
def __init__(self, httprequest):
        self.httprequest = httprequest
        self.httpresponse = None
        self.httpsession = httprequest.session
        self.disable_db = False
        self.uid = None
        self.endpoint = None
        self.endpoint_arguments = None
        self.auth_method = None
        self._cr = None

        # prevents transaction commit, use when you catch an exception during handling
        self._failed = None

        # set db/uid trackers - they're cleaned up at the WSGI
        # dispatching phase in openerp.service.wsgi_server.application
        if self.db:
            threading.current_thread().dbname = self.db
        if self.session.uid:
            threading.current_thread().uid = self.session.uid
        try:
            threading.current_thread().remote_addr = self.httprequest.remote_addr
        except Exception as ex:
            _logger.error("Canot get client ip address")
WebRequest.__init__ = __init__
