#!/usr/bin/env python
# $Id: setup.py,v 1.1 2002/01/26 22:25:04 drt Exp $
# setup for airconf
#  --drt@un.bewaff.net


from distutils.core import setup

setup(name="airconf",
            version="0.2",
            description="Python Airport Base station Configurator",
            author="Doobee R Tzeck",
            author_email="drt@un.bewaff.net",
            url="http://c0re.jp/c0de/airconf/",
            py_modules=['airport']
           )

