#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from setuptools import setup

setup(
    name='WebhookNotificationPlugin',
    version='0.2.3',
    description='Plugin to post Trac changes to a webhook',
    author='Travis Glenn Hansen',
    author_email='travisghansen@yahoo.com',
    url='https://github.com/travisghansen/trac-webhook-plugin',
    license='BSD',
    packages=['webhook_notification'],
    install_requires=[
        "requests",
    ],
    classifiers=[
        'Framework :: Trac',
        'License :: OSI Approved :: BSD License',
    ],
    entry_points={
        'trac.plugins': 'webhook_notification = webhook_notification'
    }
)
