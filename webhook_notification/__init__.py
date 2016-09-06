# -*- coding: utf-8 -*-

import json
import requests
import hashlib
import hmac
import re
from trac.core import *
from trac.config import Option, IntOption
from trac.ticket.api import ITicketChangeListener
#from trac.versioncontrol.api import IRepositoryChangeListener
#from trac.wiki.api import IWikiChangeListener

def shorten(s, length):
    result = []
    for word in s.split():
        result.append(word)
        length -= len(word)
        if length < 0:
            result.append(u"…")
            break
    return u" ".join(result)

def prepare_ticket_values(ticket, action=None):
    values = ticket.values.copy()
    values['id'] = "#" + str(ticket.id)
    values['action'] = action
    values['url'] = ticket.env.abs_href.ticket(ticket.id)
    values['project'] = ticket.env.project_name.encode('utf-8').strip()
    values['attrib'] = ''
    values['changes'] = ''
    return values

def split_option(value, separator=","):
    return map(lambda s: s.strip(), value.split(separator))


class WebhookNotificationPlugin(Component):
    implements(ITicketChangeListener)
    urls = Option('webhook', 'url', '', doc="Incoming webhook")
    fields = Option('webhook', 'fields', 'type,component,resolution',
            doc="Fields to include in notification")
    mucs = Option("webhook", "mucs", "", doc="List of MUC rooms to notify")
    jids = Option("webhook", "jids", "", doc="List of JIDs to notify")
    secret = Option("webhook", "secret", "", doc="Secret used for signing requests")
    notify_events = Option("webhook", "notify", "created,closed,changed",
            doc="List of ticket events to notify")

    def notify(self, type, values):
        values['author'] = re.sub(r' <.*', '', values['author'])
        template = u'[%(project)s] %(type)s %(id)s - %(summary)s (%(action)s by @%(author)s)'
        message = template % values

        if values['action'] == 'closed':
            message += u" ✔"

        if values['action'] == 'created':
            message += u" ⛳ "

        if values['attrib']:
            message += u" ["
            message += values['attrib']
            message += u"]"

        if values.get('changes', False):
            message += u" <"
            message += values['changes']
            message += u">"

        if values['description']:
            message += u" ✎ Description: “"
            message += shorten(re.sub(r'({{{|}}})', '', values['description']), 70)
            message += u"”"

        if values['comment']:
            message += u" ✎ Comment: “"
            message += shorten(re.sub(r'({{{|}}})', '', values['comment']), 70)
            message += u"”"

        mucs = self.mucs.strip()
        jids = self.jids.strip()

        data = {
            "mucs": map(lambda s: s.strip(), mucs.split(",")) if mucs else [],
            "jids": map(lambda s: s.strip(), jids.split(",")) if jids else [],
            "text": message.encode('utf-8').strip(),
            "url" : values["url"],
        }

        data_body = json.dumps(data).encode("utf-8")
        mac = hmac.new(self.secret.encode("utf-8"), msg=data_body, digestmod=hashlib.sha1)
        headers = {
            "Content-Type": "application/json",
            "X-WebHook-Signature": "sha1=" + mac.hexdigest(),
        }

        try:
            for url in self.urls.split(","):
                r = requests.post(url.strip(), data=data_body, headers=headers, timeout=5)
        except requests.exceptions.RequestException as e:
            return False
        return True

    def ticket_created(self, ticket):
        if not self.should_notify_event("created"):
            return
        values = prepare_ticket_values(ticket, 'created')
        values['author'] = values['reporter']
        values['comment'] = u""
        fields = (s.strip() for s in self.fields.split(','))
        attrib = (u"%s: %s" % (field, ticket[field])
                for field in fields
                if ticket[field])
        values['attrib'] = u", ".join(attrib) or u""

        self.notify('ticket', values)

    def ticket_changed(self, ticket, comment, author, old_values):
        action = 'changed'
        if 'status' in old_values:
            if 'status' in ticket.values:
                if ticket.values['status'] != old_values['status']:
                    action = ticket.values['status']

        if not self.should_notify_event(action):
            return

        values = prepare_ticket_values(ticket, action)
        values.update({
            'comment': comment or '',
            'author': author or '',
            'old_values': old_values
        })

        if 'description' not in old_values.keys():
            values['description'] = ''

        fields = self.fields.split(',')
        changes = []
        attrib = []

        for field in fields:
            if field in old_values.keys():
                if old_values[field]:
                    if ticket[field]:
                        changes.append(u'%s: %s → %s' % (field, old_values[field], ticket[field]))
                    else:
                        changes.append(u"-%s" % field)
                elif ticket[field]:
                    changes.append(u"%s: +%s" % (field, ticket[field]))
            elif ticket[field]:
                attrib.append(u"%s: %s" % (field, ticket[field]))

        values['attrib'] = u", ".join(attrib) or u""
        values['changes'] = u", ".join(changes) or u""

        self.notify('ticket', values)

    def ticket_deleted(self, ticket):
        pass

    def should_notify_event(self, event_name):
        enabled_events = set(split_option(self.notify_events))
        return len(enabled_events) == 0 or event_name in enabled_events

    #def wiki_page_added(self, page):
    #def wiki_page_changed(self, page, version, t, comment, author, ipnr):
    #def wiki_page_deleted(self, page):
    #def wiki_page_version_deleted(self, page):
