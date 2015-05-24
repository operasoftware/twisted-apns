# -*- coding: utf-8 -*-
from distutils.core import setup


setup(
  name = 'twisted-apns',
  packages = ['apns'],
  version = '0.4',
  description = 'Twisted client for Apple Push Notification Service (APNs)',
  author = 'Michał Łowicki',
  author_email = 'mlowicki@opera.com',
  url = 'https://github.com/operasoftware/twisted-apns',
  download_url = 'https://github.com/operasoftware/twisted-apns/tarball/0.4',
  keywords = ['twisted', 'apns'],
  classifiers = [],
  install_requires=['Twisted', 'pyOpenSSL']
)
