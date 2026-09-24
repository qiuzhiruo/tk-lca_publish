# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.11
#
# Description: As the description shows below
#
#export xgen file need to change 1 the "xgFileName" 2 the datapath 3 export the ma file 4 restore the oreint state
#
#
#
#
#
#
############################################

import os
import sys
import shutil
import traceback
import threading
import glob
import re
import subprocess
import production.pipeline.utils as pplu

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出植被的mel 和代理abc。"
        self.description = u"输出植被的mel 和代理abc。"
        return

    def proceed(self):
        try:
            proxy_cmd='%s %s/tools/plt/export_bbx/send_farm.py %s'%\
                                (pplu.get_dcc_launcher(proj=self.dialog.project['name'].lower(),dcc='mayapy') ,\
                                os.getenv('LC_TOOLSET'),\
                                self.dialog.version_dir)
            
            self.dialog.print_log('Run cmd %s'%(proxy_cmd))
            os.system(proxy_cmd)
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

