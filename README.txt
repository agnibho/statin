                        Statin
                        ======

What is Statin?
================

Statin is a python command line utility to generate static html websites. It
implements SSI (Server Side Inclusion) commands to generate the static files for
deployment.

Installation
============

Clone the repository to your computer and add it to your path (optional). You
need to have Python 3 installed in order to use the script.

Usage
=====

Create your website in html. The files containing SSI directives should have the
extension ".shtml", ".shtm", or ".sht". After creating the website change
directory to the document root of the site and run the script. By default the
static site will be generated in a subdirectory named statin-output.

Supported Directives
====================

A directive is written as <!--#directive parameter="value" -->

The supported directives and parameters are listed below:

Directives | Parameters
-----------|---------------------------
include    | file / virtual
exec       | cgi / cmd
echo       | var
config     | timefmt / sizefmt / errmsg
flastmod   | file / virtual
fsize      | file / virtual
printenv   | (none)
if         | expr
elif       | expr
else       | (none)
endif      | (none)
set        | var & value

Defualt Variables
=================

DATE_LOCAL
DATE_GMT
DOCUMENT_URI
DOCUMENT_NAME
LAST_MODIFIED

Configuration
=============

The default configuration is stored in the file conf.py. Available configuration
options are:

OUTPUT_DIR  : The directory where the statin output files will be saved.
PROCESS_PAT : The filename extensions recognized by statin for processing.
TIMEFMT     : The default time format.
SIZEFMT     : The default size format.
ERRMSG      : The default error message.

Licensing
=========

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

Contacts
========

Agnibho Mondal
contact@agnibho.com
www.agnibho.com
