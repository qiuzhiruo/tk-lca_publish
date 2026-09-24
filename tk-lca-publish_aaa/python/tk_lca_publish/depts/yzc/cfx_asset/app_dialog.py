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
import glob

try:
    import sgtk
    from sgtk.platform.qt import QtCore, QtGui

    # TODO
    import publish_dialog
    reload(publish_dialog)
    from publish_dialog import PublishDialog

    from ....ui.dialog import Ui_Dialog
    from ....ui.widget_sys import Ui_Form as widget_sys
    from ....ui.widget_version import Ui_Form as widget_version
    from ....ui.widget_file import Ui_Form as widget_file
    from ....ui.widget_check import Ui_Form as widget_check
    from ....ui.widget_publish import Ui_Form as widget_publish
    from widget_client_cfx_asset import Ui_Form as widget_publish_file

except:
    print traceback.format_exc()


class AppDialog(PublishDialog):
    
    def __init__(self, app):

        try:
            PublishDialog.__init__(self, app)

            # Get environment info & production info from sgtk
            self.set_vars()
            self.set_dept_vars( __file__ )

            # set up the UI, which includes the dialog and all process widgets            
            self.setup_gui(Ui_Dialog, widget_sys, widget_version, widget_file, widget_check, widget_publish, widget_publish_file)

            # setup widget functions
            self.do_bind()
            self.do_dept_bind()

            self.show_app_info()
            self.init_add_image()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())
        
        return

    def do_dept_bind(self):
        self.w_publish_file.pushButton_upload_img.clicked.connect(self.on_pick_upload)
        # self.w_publish_file.listWidget_upload_img.itemClicked.connect(self.remove_img)


    def init_add_image(self):
        proj = self.project['name'].lower()
        asset = self.entity['name']
        asset_info = self.sg.find_one('Asset', [['id', 'is', self.entity['id']]], ['sg_asset_type'])
        typee = asset_info['sg_asset_type']
        jpg_folder = '/mnt/output/projects/%s/asset/%s/%s/cfx/output/turntable/'%(proj,typee,asset)
        vers = sorted([ver for ver in os.listdir(jpg_folder) if os.path.isdir(os.path.join(jpg_folder,ver)) and ver.startswith('v')])
        if vers:
            latest_ver = vers[-1]
        img_list = glob.glob(jpg_folder + latest_ver + '/*_yzc.jpg')
        print img_list
        for i in img_list:
            self.w_publish_file.listWidget_upload_img.addItem(i)

    def on_pick_upload(self):
        root_dir = self.work_root.replace('/task/maya', '/output/turntable').replace('/mnt/work','/output')
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        pick_dialog.setNameFilter(("Images (*.jpg)"))
        pick_dialog.setDirectory(root_dir)
        pick_dialog.exec_()

        spm_file_list = pick_dialog.selectedFiles()
        for spm_file in spm_file_list:
            if os.path.isfile(spm_file):
                self.w_publish_file.listWidget_upload_img.addItem(spm_file)

        return
    
    def remove_img(self):
        l_items = self.w_publish_file.listWidget_upload_img.selectedItems()

        for item in l_items:
            i = self.w_publish_file.listWidget_upload_img.indexFromItem(item).row()
            self.w_publish_file.listWidget_upload_img.takeItem(i)

        return



