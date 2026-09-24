# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.08
#
# Description: 
#
############################################

import os
import traceback
import shutil
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将pubish文件中reference的模型变成import。"
        self.description = u"非chr类资产中如果直接reference了模型，在最终下游组使用文件中把模型import进来，减少reference层级。"
        return


    def proceed(self):
        try:
            #print '<import_ref>'
            #print asset_info
            if self.dialog.asset_type != 'chr':
                # asset's locking relies on this condition, any asset who failed to meet this condition will not be locked neither
                mayapy = os.environ['MAYA_LOCATION'] + '/bin/mayapy'
                export_script = os.path.dirname(__file__).replace('\\', '/') + '/rig_export.py'

                sub_folder = 'ref'
                if not pm.referenceQuery('|master', isNodeReferenced=True):
                    sub_folder = 'backup'

                if not os.path.isdir(self.dialog.version_dir + '/' + sub_folder):
                    os.makedirs(self.dialog.version_dir + '/' + sub_folder)

                ref_ma = self.dialog.version_dir + '/'+sub_folder+'/' + self.dialog.entity['name'] + '.ma'

                shutil.copyfile(self.dialog.tank_file, ref_ma)
                cmd_str = '"' + mayapy + '" ' + export_script + ' ' + ref_ma + ' ' + self.dialog.tank_file + ' hi'
                print 'Command string:', cmd_str
                os.system(cmd_str)

                if not os.path.isfile(self.dialog.tank_file):
                    self.dialog.print_log(u"没能导入模型reference", txt_color = QtGui.QColor(255, 150, 30) )

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description



