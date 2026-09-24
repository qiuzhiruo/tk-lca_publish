# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.11
#
# Description: 
#
############################################

import os
import re
import subprocess
import traceback


# tool_srf_path='/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/srf_sg'
tool_srf_path='/home/yingjie/git_repo/tk-lca-publish/python/tk_lca_publish/publish_process/srf_sg'

def get_ma_version(maya_file):
    with open(maya_file,'r') as f:
        lines='a'
        while lines:
            lines=f.readline()
            if lines.startswith('requires maya'):
                return re.findall('requires maya "(\d{4})".*', lines)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"Publish srf Maya ma file."
        self.description = u"Publish srf Maya ma file."
        return


    def proceed(self):
        try:
            in_ma=str(self.dialog.w_publish_file.lineEdit_ma_file.text())
            if not in_ma or not os.path.isfile(in_ma):
                return
                
            asset_name=os.path.basename(self.dialog.katana_file)
            asset_name=asset_name.split('.')[0]
            out_ma=os.path.join(self.dialog.version_dir,asset_name+'.ma')

            self.dialog.print_log('Begin export maya ma file.'+in_ma+' -> '+out_ma)
            
            maya_version=get_ma_version(in_ma)
            if not maya_version:
                maya_version=['2013']

            mayapy='/mnt/usr/autodesk/maya'+maya_version[0]+'-x64/bin/mayapy'
            if not os.path.isfile(mayapy):
                return ('Cannot find mayapy '+mayapy)

            cmd=[mayapy,tool_srf_path+'/export_ma.py',in_ma,out_ma]
            p1=subprocess.Popen(cmd,stdout = subprocess.PIPE)
            line = 'Start Eport...'
            while line != "":
                line = p1.stdout.readline()
                if 'Srf export Error:' in line:
                    return line
            p1.wait()

            return ''

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


