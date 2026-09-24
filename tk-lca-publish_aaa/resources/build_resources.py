# -*- coding:utf-8 -*-
import os
import sys

root = os.path.split(__file__)[0].replace("\\", '/')
dst = root.replace('/resources', '/python/tk_lca_publish/ui/')


l_files = os.listdir(root)

white_list = ['widget_file_hyperloop.ui',
        ]

for file_name in l_files:
    if not file_name in white_list:
        continue
    if file_name.endswith('.ui'):
        new_file = dst + file_name[:-3] + '.py'
        cmdStr = 'pyuic4 '+root + '/' + file_name + ' -o ' + new_file

        os.system(cmdStr)

        f = open(new_file, 'r')
        f_content = f.read().replace("from PyQt4 import", "from sgtk.platform.qt import")
        f.close()

        #print f_content
        #print dir(f)

        f = open(new_file, 'w')
        f.write(f_content)
        f.close()

        print 'Export:', new_file

