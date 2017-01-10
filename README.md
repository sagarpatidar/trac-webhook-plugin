# trac-webhook-plugin

Plugin to post Trac changes to a webhook endpoint.
The goal is to provide a complete dataset for as many events as possible.

Currently 2 resource types are supported:
 1. Tickets
 1. WikiPage

## Installation

Requirements:

* [Requests](https://pypi.python.org/pypi/requests)

```
python setup.py bdist_egg;
cp dist/WebhookNotificationPlugin-0.2.1-py2.7.egg /path/to/plugins
```

Install and enable the plugin in `trac.ini`:

```ini
[components]
webhook_notification.* = enabled
```

Configuration in trac.ini:

```ini
[webhook]
secret = randomstring
url = https://host/webhook/path
username = HTTP Auth Username
password = HTTP Auth Password
```

Some notes on the configuration:

* The `secret` must be a random string which is configured also in the
  receiving endpoint. It is used to generate a HMAC-SHA1 hex digest of the
  body using `secret` as the key. The digest is sent in the
  `X-WebHook-Signature` HTTP header.

## Data Format
All events publish the following standard fields: 
```
{
   "_event":{
      "action":"see list of per-realm actions",
      "realm":"wiki|ticket",
      "invoke_url":"url that generated the event",
      "project":{
         "admin":"admin@awesome.com",
         "description":"Awesome Project",
         "name":"Awesome",
         "url":"https://trac.awesome.com"
      },
      "resource_url":"url to either the target ticket or wiki page",
      "user":{
         "email":"user@awesome.com",
         "name":"user who instigated the change",
         "username":"user"
      }
   }
   ...
}
```
If the realm is `ticket` then additionally there will be a top-level key `ticket` which includes all the ticket details.

If the realm is `wiki` then addtionally there will be a top-level key `page` which includes all the wiki page details.

If the action is an `attachment` action then the result will include the appropriate top-level key for either `ticket` or `wiki` **and** additionally an `attachment` top-level key with the details of the `attachment`.

Various *action specific* top-level keys (eg: if a `ticket` `changed` event is triggered there will be an `old_values` top-level key with all the changes).


## Development

```python setup.py develop --multi-version --exclude-scripts --install-dir /path/to/plugins/```

## Acknowledgements

This plugin is based on the [trac-webhook-plugin](https://github.com/aperezdc/trac-webhook-plugin),
which is based on the [Slack Notification plugin](https://github.com/mandic-cloud/trac-slack-plugin),
which is based on the [Irker Notification plugin](https://github.com/Southen/trac-irker-plugin).
Lots of thanks go to their authors!


## License

```
Copyright (c) 2016, Adrián Pérez de Castro <aperez@igalia.com>
Copyright (c) 2014, Sebastian Southen
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in
   the documentation and/or other materials provided with the
   distribution.
3. The name of the author may not be used to endorse or promote
   products derived from this software without specific prior
   written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR `AS IS'' AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```
