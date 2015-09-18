# -*- coding: utf-8 -*-
from distutils.core import setup


VERSION = '0.13'
URL = 'https://github.com/operasoftware/twisted-apns'
DOWNLOAD_URL = URL + '/tarball/' + VERSION


setup(
  name = 'twisted-apns',
  packages = ['apns'],
  version = VERSION,
  description = 'Twisted client for Apple Push Notification Service (APNs)',
  author = 'Michał Łowicki',
  author_email = 'mlowicki@opera.com',
  url = URL,
  download_url = DOWNLOAD_URL,
  keywords = ['twisted', 'apns'],
  classifiers = [],
  install_requires=['Twisted', 'pyOpenSSL']
)
