import os
import zipfile
from xml.dom import minidom


def create_zip(filename, foldername):
    zf = zipfile.ZipFile(filename, "w")
    for dirname, subdirs, files in os.walk(foldername):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()


def get_version(foldername):
    xmldoc = minidom.parse('%s/addon.xml' % foldername)
    itemlist = xmldoc.getElementsByTagName('addon')
    version = itemlist[0].attributes['version'].value
    return version


foldername = "plugin.image.shotwell"
version = get_version(foldername)
filename = "xbmc-shotwell-%s.zip" % version
create_zip(filename, foldername)
