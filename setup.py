#!/usr/bin/env python

from setuptools import setup

setup(name='tap-appstore',
      version='0.2.0',
      description='Singer.io tap for extracting data from the App Store Connect API',
      author='JustEdro',
      url='https://github.com/JustEdro',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap-appstore'],
      install_requires=[
          'singer-python @ git+https://github.com/peliqan-io/singer-python@master',
          'appstoreconnect @ git+https://github.com/Peliqan-io/appstoreconnectapi@change/key_file_as_string',
          'pytz==2018.4',
          'dateparser==1.1.8'
      ],
      entry_points='''
          [console_scripts]
          tap-appstore=tap_appstore:main
      ''',
      packages=['tap_appstore'],
      package_data={
          'tap_appstore/schemas': [
              'summary_sales_report.json'
          ],
      },
      include_package_data=True,
      )
