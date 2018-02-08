#! /usr/bin/env python3

'''
Copyright (c) 2018 Agnibho Mondal
All rights reserved

This file is part of Statin.

Statin is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Statin is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Statin.  If not, see <http://www.gnu.org/licenses/>.
'''

from setuptools import setup

setup(name = "statin",
      version = "1.0",
      description = "Static html files generator",
      author = "Agnibho Mondal",
      author_email = "contact@agnibho.com",
      url = "https://code.agnibho.com/statin/",
      packages = ["statin"],
      entry_points = {"console_scripts" : ["statin = statin.statin:main"]},
      long_description = "Statin is a static html files generator. It is compatible with SSI directives.",
      classifiers = [
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Natural Language :: English",
          "Operating System :: POSIX",
          "Operating System :: Unix",
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Software Development :: Code Generators"
          ]
      )
