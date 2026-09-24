# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.05
#
# Description: 
#
############################################

import os
import traceback
import shutil
import pymel.core as pm
from sgtk.platform.qt import QtGui

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"道具/场景拆出一个低模绑定。"
        self.description = u"拆出的低模绑定可以帮助 Layout/Ani 减少读取场景时间，加快制作过程。"
        return


    def proceed(self):
        try:
            #self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'
            asset_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])
            if asset_info['sg_asset_type'] != 'chr':
                if not os.path.isdir( self.dialog.version_dir + '/res_lo' ):
                    os.makedirs(self.dialog.version_dir + '/res_lo')
                mayapy = os.environ['MAYA_LOCATION'] + '/bin/mayapy'
                export_script = os.path.dirname(__file__).replace('\\', '/') + '/rig_export.py'
                lo_res = self.dialog.version_dir + '/res_lo/' + self.dialog.entity['name'] + '.ma'
                cmd_str = '"' + mayapy + '" ' + export_script + ' ' + self.dialog.tank_file + ' ' + lo_res + ' lo'
                print 'Command string:', cmd_str
                os.system(cmd_str)

                if not os.path.isfile(lo_res):
                    self.dialog.print_log(u"没能输出 rig 的lo模", txt_color = QtGui.QColor(255, 150, 30) )

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


