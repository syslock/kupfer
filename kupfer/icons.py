from os import path

icon_cache = {}

def get_icon(key):
	"""
	try retrieve icon in cache
	is a generator so it can be concisely called with a for loop
	"""
	if key not in icon_cache:
		return
	rec = icon_cache[key]
	rec["accesses"] += 1
	yield rec["icon"]

def store_icon(key, icon):
	if key in icon_cache:
		raise Exception("already in cache")
	icon_rec = {"icon":icon, "accesses":0}
	icon_cache[key] = icon_rec

def get_icon_for_gicon(gicon, icon_size):
	# FIXME: We can't load any general GIcon
	from gio import File, FILE_ATTRIBUTE_STANDARD_ICON, ThemedIcon, FileIcon
	if isinstance(gicon, FileIcon):
		ifile = gicon.get_file()
		return get_icon_from_file(ifile.get_path(), icon_size)
	if isinstance(gicon, ThemedIcon):
		names = gicon.get_names()
		return get_icon_for_name(names[0], icon_size, names)
	print "get_icon_for_gicon, could not load", gicon
	return None

def get_icon_for_uri(uri, icon_size):
	"""
	Return a pixbuf representing the file at
	the URI generally (mime-type based)

	return None if not found
	
	@param icon_size: a pixel size of the icon
	@type icon_size: an integer object.
	 
	"""
	from gtk import icon_theme_get_default
	from gio import File, FILE_ATTRIBUTE_STANDARD_ICON, ThemedIcon, FileIcon

	icon_theme = icon_theme_get_default()
	gfile = File(uri)
	if not gfile.query_exists():
		return None

	finfo = gfile.query_info(FILE_ATTRIBUTE_STANDARD_ICON)
	gicon = finfo.get_attribute_object(FILE_ATTRIBUTE_STANDARD_ICON)
	return get_icon_for_gicon(gicon, icon_size)

def get_icon_for_name(icon_name, icon_size, icon_names=[]):
	for i in get_icon(icon_name):
		return i
	from gtk import icon_theme_get_default, ICON_LOOKUP_USE_BUILTIN, ICON_LOOKUP_FORCE_SIZE
	from gobject import GError
	icon_theme = icon_theme_get_default()
	if not icon_names: icon_names = (icon_name,)

	# Try the whole list of given names, without extension
	rmext = lambda n: path.splitext(n)[0]
	for load_name in (rmext(name) for name in icon_names):
		try:
			icon = icon_theme.load_icon(load_name, icon_size, ICON_LOOKUP_USE_BUILTIN | ICON_LOOKUP_FORCE_SIZE)
			if icon:
				break
		except GError, e:
			icon = None
		except Exception, e:
			print "get_icon_for_name, error:", e
			icon = None
	else:
		# if we did not reach 'break' in the loop
		return None
	# We store the first icon in the list, even if the match
	# found was later in the chain
	store_icon(icon_name, icon)
	return icon

def get_icon_for_desktop_file(desktop_file, icon_size):
	"""
	Return the icon of a given desktop file path
	"""
	from gnomedesktop import item_new_from_file, LOAD_ONLY_IF_EXISTS
	desktop_item = item_new_from_file(desktop_file, LOAD_ONLY_IF_EXISTS)

	return get_icon_for_desktop_item(desktop_item, icon_size)

def get_icon_for_desktop_name(desktop_name, icon_size):
	"""
	Return the icon of a desktop item given its basename
	"""
	for icon in get_icon(desktop_name):
		return icon
	from gnomedesktop import item_new_from_basename, LOAD_ONLY_IF_EXISTS
	desktop_item = item_new_from_basename(desktop_file, LOAD_ONLY_IF_EXISTS)

	icon = get_icon_for_desktop_item(desktop_item, icon_size)
	store_icon(desktop_name, icon)
	return icon

def get_icon_for_desktop_item(desktop_item, icon_size):
	"""
	Return the pixbuf of a given desktop item

	Use some hackery. Take the icon directly if it is absolutely given,
	otherwise use the name minus extension from current icon theme
	"""
	from gtk import icon_theme_get_default
	from gnomedesktop import find_icon, LOAD_ONLY_IF_EXISTS, KEY_ICON
	icon_name = desktop_item.get_string(KEY_ICON)
	if not icon_name:
		return None

	if not path.isabs(icon_name):
		icon_name, extension = path.splitext(icon_name)
		icon_info = icon_theme_get_default().lookup_icon(icon_name, icon_size, 0)
		if icon_info:
			icon_file = icon_info.get_filename()
		else:
			icon_file = None
	else:
		icon_file = icon_name

	if not icon_file:
		return None
	return get_icon_from_file(icon_file, icon_size)


def get_icon_from_file(icon_file, icon_size):
	# try to load from cache
	for icon in get_icon(icon_file):
		return icon

	from gtk.gdk import pixbuf_new_from_file_at_size
	from gobject import GError
	try:
		icon = pixbuf_new_from_file_at_size(icon_file, icon_size, icon_size)
		store_icon(icon_file, icon)
		return icon
	except GError, e:
		print "get_icon_from_file, error:", e
		return None

def get_default_application_icon(icon_size):
	icon = get_icon_for_name("exec", icon_size)
	return icon
