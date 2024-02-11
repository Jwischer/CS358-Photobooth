import setuptools

setuptools.setup(name='FrontendPackage',
version='0.1',
description='Package that contains frontend functions for the Union Photobooth',
url='#',
author='Jake Wischer',
install_requires=['pyautogui','opencv-python', 'RPi.GPIO', 'pathlib'],
author_email='jake.wischer@valpo.edu',
packages=setuptools.find_packages(),
zip_safe=False)