# -*- coding:utf-8 -*-
__author__ = 'yingjie'

import os
import traceback
import shutil
import getpass

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"标记植被dynamic archive"
        self.description  = u"如果srf已经出了xgen archive，我们将写出一个文件，用来标记需要重刷dynamic archvie"
        return


    def proceed(self):
        try:
            proj_dir=os.getenv('LC_PROJ')
            plt_dir=proj_dir+'/trash/plt_archive'
            mod_dir=proj_dir+'/trash/plt_archive/mod_dynamic'
            mark_file_name=self.dialog.project['name'].lower() +'.'+ self.dialog.entity['name']
            mod_mark_file=mod_dir+'/'+mark_file_name+'.'+getpass.getuser()

            if os.path.isfile(plt_dir+'/'+mark_file_name):
                with open(mod_mark_file ,'w') as f:
                    pass
                try:
                    os.chmod(mod_mark_file, 0777)
                except:
                    pass
                self.dialog.print_log(u'发现srf已经publish过archive，标记文件到'+mod_mark_file)
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
