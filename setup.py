#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from setuptools import setup

setup(
    name='WebhookNotificationPlugin',
    version='0.2',
    description='Plugin to post Trac changes to a webhook',
    author='Adrián Pérez de Castro',
    author_email='aperez@igalia.com',
    url='https://github.com/aperezdc/trac-webhook-plugin',
    license='BSD',
    packages=['webhook_notification'],
    classifiers=[
        'Framework :: Trac',
        'License :: OSI Approved :: BSD License',
    ],
    entry_points={
        'trac.plugins': 'webhook_notification = webhook_notification'
    }
)
