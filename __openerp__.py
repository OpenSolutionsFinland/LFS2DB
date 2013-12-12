
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Open Solutions Finland 2013.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Local Filesystem data importer",
    "version" : "1.0",
    "author" : "Open Solutions Finland",
    "description" : """
*** Local Filesystem data importer ***
OpenERP module for importing data from local file system to database
***********************************
    """,
    "website" : "http://www.opensolutions.fi",
    "depends" : ["base","mrp", "message_box"],
    "category" : "General",
    "init_xml" : [],
    "demo_xml" : [],
    "data" : [
              'lfs2db_view.xml',

                    ],
    'test': [
             ],
    'installable': True,
    'active': False,
    'certificate': '',
}
