# trac-webhook-plugin

Plugin to post Trac changes to a webhook endpoint.

## Installation

Requirements:

* [Requests](https://pypi.python.org/pypi/requests)

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

* The plugin emits the following data/events
 * Ticket
   * created
   * changed
   * deleted
 * Wiki
  * created
  * changed

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
