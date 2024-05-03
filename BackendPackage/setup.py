#setup.py  Copyright (C) 2024  Valparaiso University

import setuptools

setuptools.setup(name='BackendPackage',
version='0.1',
description='Package that contains backend functions for the Union Photobooth',
url='#',
author='Jake Wischer',
install_requires=['pandas','pathlib','google-api-python-client','oauth2client','google_auth_oauthlib'],
author_email='jake.wischer@valpo.edu',
packages=setuptools.find_packages(),
zip_safe=False)
