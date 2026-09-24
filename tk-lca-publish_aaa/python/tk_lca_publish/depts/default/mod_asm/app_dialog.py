# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: model publish tool. 
#
########################################################################################

import os
import sys
import pprint
import shutil
import traceback
import time
import getpass
import pymel.core as pm

try:
    import sgtk
    from sgtk.platform.qt import QtCore, QtGui

    # TODO
    import publish_dialog

    reload(publish_dialog)
    from publish_dialog import PublishDialog

    from ....ui.dialog import Ui_Dialog
    from ....ui.widget_sys import Ui_Form as widget_sys
    from ....ui.widget_file import Ui_Form as widget_file
    from ....ui.widget_version import Ui_Form as widget_version
    from ....ui.widget_check import Ui_Form as widget_check
    from ....ui.widget_publish import Ui_Form as widget_publish

    from ....ui.widget_file_mod import Ui_Form as widget_publish_file

except:
    print traceback.format_exc()


class AppDialog(PublishDialog):
    def __init__(self, app):

        try:
            PublishDialog.__init__(self, app)

            # Get environment info & production info from sgtk
            self.set_vars()
            self.set_dept_vars(__file__)

            # set up the UI, which includes the dialog and all process widgets            
            self.setup_gui(Ui_Dialog, widget_sys, widget_version, widget_file, widget_check, widget_publish,
                           widget_publish_file)

            # setup widget functions
            self.do_bind()

            self.w_sys.comboBox_tag.currentIndexChanged.connect(self.set_publish_mode_tag)

            self.show_app_info()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())
        
        return


    def set_publish_mode_tag(self):
        if self.ui.comboBox_publish_mode.currentIndex() in [0,1]:
            self.set_publish_mode()

    def get_omit_check(self, check):
        if self.step['name'] in ['mod'] and self.w_sys.comboBox_tag.currentIndex() == 0:
            mod_type = self.sg.find_one('Asset', [['id', 'is', self.entity['id']]], ['sg_asset_type'])['sg_asset_type']

            omit_mod_list = ['chr_camera_check', 'light_check', 'check_hair_patch', 'dynamic_file_name', 'lod_match',
                             'one_shaer_per', 'extremely_short_edge', 'uv_holes', 'light_check',
                             'exceed_range_uv', 'asm_mesh', "light_check"]

            if check.module_name in omit_mod_list and mod_type in ['asm', 'chr', 'crd']:
                return True

        if self.step['name'] in ['mod', 'asm'] and self.w_sys.comboBox_tag.currentIndex() == 2:

            mod_type = self.sg.find_one('Asset', [['id', 'is', self.entity['id']]], ['sg_asset_type'])['sg_asset_type']
            omit_mod_list = ["mesh_name", "pivot_on_orgion", "no_empty_trans", "unknown_nodes",
                             "light_check", "symmetrical_check", "chr_camera_check", "normal_is_checked",
                             "character_shaders","unique_name","transform_name"]

            if check.module_name in omit_mod_list and mod_type in ['asm', 'chr', 'crd']:
                return True

        return False

    def auto_dynamic(self):
        #asset_info = self.sg.find_one('Asset', [['id', 'is', self.entity['id']]], ['sg_asset_type'])
        #if asset_info['sg_asset_type'] == 'flg':
        self.w_publish_file.pushButton_dy.setEnabled(1)
        self.w_publish_file.pushButton_dy_export.setEnabled(1)
        self.w_publish_file.start_f.setEnabled(1)
        self.w_publish_file.end_f.setEnabled(1)
        self.w_publish_file.label_s.setEnabled(1)
        self.w_publish_file.label_e.setEnabled(1)
        return
