# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: John Su
#
# Date: 2013.11
#
# Description: As the description shows below
#
############################################

import os
import traceback
import shutil
import re


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"复制City Cache"
        self.description = u"保持层级复制cache"

    def output(self, msg):
        self.dialog.print_log(msg)

    def replaceFileText(self, file_to_process, src, tgt):
        with open(file_to_process) as f:
            data = f.read().replace(src, tgt)
        with open(file_to_process, 'w') as f:
            f.write(data)

    def proceed(self):
        try:
            dir_path = self.dialog.w_publish_file.listWidget_cache.item(0).text().rstrip('/')
            target_dir = self.dialog.version_dir.rstrip('/')
            self.output(target_dir)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            os.system('cp -r %s %s' % (dir_path, target_dir))

            #src = re.findall(r'(.*)/[\d\w]*\..*\..*\.v\d{3}$', dir_path)[0]
            for dp, dn, files in os.walk(target_dir):
                files_to_modify = [os.path.join(dp, f) for f in files if (f.endswith('.ma') or f.endswith('.xml'))]
                for f in files_to_modify:
                    self.replaceFileText(f, dir_path, target_dir)

            return ""
        except:
            self.output(u'publish错误，请检查路径是否符合标准.')
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


