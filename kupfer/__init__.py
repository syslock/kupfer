#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
kupfer      A quick hack and a launcher
ɹǝɟdnʞ

Copyright 2007--2009 Ulrik Sverdrup <ulrik.sverdrup@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

if __name__ == '__main__':
	from kupfer import main
	print "\n".join(__doc__.splitlines()[:11])
	main.main()
