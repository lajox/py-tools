# -*- coding: utf-8 -*-

import sys
sys.path.append('..')
from version import *
import re

versioninfo_file = 'versioninfo.txt'
versioninfo_config = {
    'CompanyName': 'py-tools工具箱',
    'FileDescription': 'py-tools工具箱',
    'InternalName': 'py-tools工具箱',
    'LegalCopyright': 'Copyright(C) 2024 py-tools工具箱',
    'OriginalFilename': 'tool',
    'ProductName': 'py-tools工具箱',
}

def process_version_info():
    current_version = APP_VERSION
    ver = current_version.split('.')
    config = versioninfo_config
    with open(versioninfo_file, 'r+', encoding='utf8') as ver_file:
        txt = ver_file.read()
        txt = re.sub("filevers=\\(\\d+, \\d+, \\d+, \\d+\\),", f"filevers=({ver[0]}, {ver[1]}, {ver[2]}, {ver[3]}),", txt)
        txt = re.sub("prodvers=\\(\\d+, \\d+, \\d+, \\d+\\),", f"prodvers=({ver[0]}, {ver[1]}, {ver[2]}, {ver[3]}),", txt)

        txt = re.sub("StringStruct\\(u?'CompanyName',\s*u?'.+?'\\)", f"StringStruct(u'CompanyName', u'{config['CompanyName']}')", txt)
        txt = re.sub("StringStruct\\(u?'FileDescription',\s*u?'.+?'\\)", f"StringStruct(u'FileDescription', u'{config['FileDescription']}')", txt)
        txt = re.sub("StringStruct\\(u?'InternalName',\s*u?'.+?'\\)", f"StringStruct(u'InternalName', u'{config['InternalName']}')", txt)
        txt = re.sub("StringStruct\\(u?'LegalCopyright',\s*u?'.+?'\\)", f"StringStruct(u'LegalCopyright', u'{config['LegalCopyright']}')", txt)
        txt = re.sub("StringStruct\\(u?'OriginalFilename',\s*u?'.+?'\\)", f"StringStruct(u'OriginalFilename', u'{config['OriginalFilename']}')", txt)
        txt = re.sub("StringStruct\\(u?'ProductName',\s*u?'.+?'\\)", f"StringStruct(u'ProductName', u'{config['ProductName']}')", txt)

        txt = re.sub("StringStruct\\(u?'FileVersion',\s*u?'.+?'\\)", f"StringStruct(u'FileVersion', u'{current_version}')", txt)
        txt = re.sub("StringStruct\\(u?'ProductVersion',\s*u?'.+?'\\)", f"StringStruct(u'ProductVersion', u'{current_version}')", txt)
        txt = re.sub("StringStruct\\(u?'SpecialBuild',\s*u?'.+?'\\)", f"StringStruct(u'SpecialBuild', u'{ver[3]}')", txt)
        ver_file.seek(0)
        ver_file.truncate()
        ver_file.write(txt)
    pass

if __name__ == "__main__":
    process_version_info()
    print('versioninfo.txt has been updated.')