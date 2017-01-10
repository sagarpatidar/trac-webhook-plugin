# -*- coding: utf-8 -*-

import json
import requests
import hashlib
import hmac
import re
from collections import OrderedDict
from trac.core import *
from trac.config import Option, BoolOption, IntOption
from trac.util.datefmt import to_utimestamp
from trac.ticket.api import ITicketChangeListener
from trac.ticket.model import Ticket
from trac.attachment import IAttachmentChangeListener
from trac.wiki.api import IWikiChangeListener
from trac.wiki.model import WikiPage
from trac.web.api import IRequestFilter

class SortedDict(OrderedDict):

    def __init__(self, **kwargs):
        super(SortedDict, self).__init__()

        for key, value in sorted(kwargs.items()):
            if isinstance(value, dict):
                self[key] = SortedDict(**value)
            else:
                self[key] = value

def prepare_ticket_values(ticket):
    values = ticket._to_db_types(ticket.values)
    values['id'] = ticket.id
    return values

def prepare_wiki_page_values(page):
    values = {
        "name": page.name,
        "version": page.version,
        "time": to_utimestamp(page.time),
        "author": page.author,
        "text": page.text,
        "comment": page.comment,
        "readonly": page.readonly,
    }
    return values

def prepare_attachment_values(attachment):
    values = {
        "parent_realm": attachment.parent_realm,
        "parent_id": attachment.parent_id,
        "filename": attachment.filename,
        "size": attachment.size,
        "date": to_utimestamp(attachment.date),
        "description": attachment.description,
        "author": attachment.author,
    }
    return values

class WebhookNotificationPlugin(Component):
    implements(ITicketChangeListener, IWikiChangeListener, IAttachmentChangeListener, IRequestFilter)
    url = Option('webhook', 'url', '', doc='Outgoing webhook URL')
    secret = Option('webhook', 'secret', '', doc='Secret used for signing requests')
    username = Option('webhook', 'username', '', doc='Username for HTTP Auth')
    password = Option('webhook', 'password', '', doc='Password for HTTP Auth')
    ssl_verify = BoolOption('webhook', 'ssl_verify', 'true', doc='Verify server SSL certificate')
    req = None

    def notify(self, realm, action, values):
        values['_event'] = {
            'realm': realm,
            'action': action,
            'user': {
                'username': self.req.authname,
                'name': self.req.session.get('name'),
                'email': self.req.session.get('email'),
            },
            'project': {
                'name': self.env.project_name.encode('utf-8').strip(),
                'description': self.env.project_description.encode('utf-8').strip(),
                'admin': self.env.project_admin.encode('utf-8').strip(),
                'url': self.env.project_url,
                'icon': self.env.project_icon,
                'base_url': self.env.abs_href(),
            },
            'invoke_url': self.req.base_url + self.req.path_info,
        }

        if realm == 'ticket':
            values['_event']['resource_url'] = self.env.abs_href('ticket', values['ticket']['id'])
        elif realm == 'wiki':
            values['_event']['resource_url'] = self.env.abs_href('wiki', values['page']['name'])

        # make the dict sorted for readability
        values = SortedDict(**values)
        data_body = json.dumps(values).encode("utf-8")
        mac = hmac.new(self.secret.encode("utf-8"), msg=data_body, digestmod=hashlib.sha1)
        headers = {
            "Content-Type": "application/json",
            "X-WebHook-Signature": "sha1=" + mac.hexdigest(),
        }

        try:
            # for client cert
            # cert=('/path/client.cert', '/path/client.key')
            r = requests.post(self.url.strip(), data=data_body, headers=headers, timeout=5, auth=(self.username, self.password), verify=self.ssl_verify)
        except requests.exceptions.RequestException as e:
            #self.log.error("Failed webhook request: %r", e)
            return False
        return True

    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        self.req = req
        return handler
    
    def post_process_request(self, req, template, data, content_type):
        return template, data, content_type

    # ITicketChangeListener methods
    def ticket_created(self, ticket):
        values = {
            'author': u"",
            'comment': u"",
            'old_values': {},
            'ticket': prepare_ticket_values(ticket),
        }
        self.notify('ticket', 'created', values)

    def ticket_changed(self, ticket, comment, author, old_values):
        action = 'changed'
        if 'status' in old_values:
            if 'status' in ticket.values:
                if ticket.values['status'] != old_values['status']:
                    action = ticket.values['status']

        values = {
            'author': author or '',
            'comment': comment or '',
            'old_values': ticket._to_db_types(old_values),
            'ticket': prepare_ticket_values(ticket),
        }
        self.notify('ticket', action, values)

    def ticket_deleted(self, ticket):
        values = {
            'ticket': prepare_ticket_values(ticket),
        }
        self.notify('ticket', 'deleted', values)

    def ticket_comment_modified(self, ticket, cdate, author, comment, old_comment):
        pass

    def ticket_change_deleted(self, ticket, cdate, changes):
        pass

    def _unlock_achievement(self, user, name):
        pass

    # IWikiChangeListener methods
    def wiki_page_added(self, page):
        values = {
            'page': prepare_wiki_page_values(page),
        }
        self.notify('wiki', 'created', values)

    def wiki_page_changed(self, page, version, t, comment, author, ipnr):
        values = {
            'page': prepare_wiki_page_values(page),
        }
        self.notify('wiki', 'changed', values)

    def wiki_page_deleted(self, page):
        values = {
            'page': prepare_wiki_page_values(page),
        }
        self.notify('wiki', 'deleted', values)

    # can only delete the most recent version
    # so deleted revision = page.version + 1
    def wiki_page_version_deleted(self, page):
        values = {
            'page': prepare_wiki_page_values(page),
        }
        self.notify('wiki', 'version deleted', values)

    def wiki_page_renamed(self, page, old_name):
        values = {
            'old_name': old_name,
            'page': prepare_wiki_page_values(page),
        }
        self.notify('wiki', 'renamed', values)

    def wiki_page_comment_modified(self, page, old_comment):
        values = {
            'old_comment': old_comment,
            'page': prepare_wiki_page_values(page),
        }
        self.notify('wiki', 'comment modified', values)

    # IAttachmentChangeListener methods
    def _attachment_action(self, attachment, action):
        parent = attachment.resource.parent
        if parent.realm == "ticket":
            ticket = Ticket(self.env, parent.id)
            values = {
                'ticket': prepare_ticket_values(ticket),
                'attachment': prepare_attachment_values(attachment),
            }
        elif parent.realm == "wiki":
            page = WikiPage(self.env, parent.id)
            values = {
                'page': prepare_wiki_page_values(page),
                'attachment': prepare_attachment_values(attachment),
            }
        
        if parent.realm == "ticket" or parent.realm == "wiki":
            self.notify(parent.realm, action, values)

    def attachment_added(self, attachment):
        self._attachment_action(attachment, 'attachment added')

    def attachment_deleted(self, attachment):
        self._attachment_action(attachment, 'attachment deleted')

    def attachment_reparented(self, attachment, old_parent_realm, old_parent_id):
        pass
