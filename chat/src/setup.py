'''
Created on Jan 30, 2014

@author: anya
'''

from setuptools import setup, find_packages
setup(name='chat',
      packages=find_packages(),
      scripts = ["scripts/stert_server.py", "scripts/stert_client.py"],
      version=0.1)
