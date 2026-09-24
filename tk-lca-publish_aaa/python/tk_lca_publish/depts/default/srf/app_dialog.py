# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Art publish tool. Create version on server and shtogun
#              This is the first publish tool in the LCA. All publish tools of
#              different departments will share:
#              Gui widgets; system check module; version check module
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

    import publish_dialog

    reload(publish_dialog)
    from publish_dialog import PublishDialog

    from ....ui.dialog import Ui_Dialog
    from ....ui.widget_sys import Ui_Form as widget_sys
    from ....ui.widget_version import Ui_Form as widget_version
    from ....ui.widget_file import Ui_Form as widget_file
    from ....ui.widget_check import Ui_Form as widget_check
    from ....ui.widget_publish import Ui_Form as widget_publish

    from ....ui.widget_file_srf import Ui_Form as widget_publish_file

except:
    print traceback.format_exc()

QT_GUI_BASE = ('PySide.QtGui', 'PySide2.QtGui', 'PyQt4.QtGui', 'PyQt5.QtGui')


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

            # TODO Can't use the thumbnail widget outside Maya
            self.w_file.thumbnail_widget.setEnabled(False)

            # setup widget functions
            self.do_bind()
            self.do_dept_bind()
            self.show_app_info()
            self.push_shader_enable()


        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            self._app.log_error(traceback.format_exc())

        return

    def do_dept_bind(self):
        self.w_publish_file.checkBox.stateChanged.connect(self.enable_xml_publish)

    def enable_xml_publish(self):
        if int(self.w_publish_file.checkBox.isChecked()):
            self.w_publish_file.checkBox_xgenarc.setEnabled(False)
            self.w_publish_file.checkBox_shader.setEnabled(False)
            self.w_publish_file.checkBox_shader.setChecked(False)
        else:
            self.w_publish_file.checkBox_xgenarc.setEnabled(True)
            self.w_publish_file.checkBox_shader.setEnabled(True)

    def xgenarc_enable(self):
        asset_type = self.work_root.replace('\\', '/').split('/')[6]
        if asset_type == 'flg':
            self.w_publish_file.checkBox_xgenarc.setChecked(True)

    def push_shader_enable(self):

        asset_info = self.sg.find_one('Asset', [['id', 'is', self.entity['id']]], ['sg_diffculty2', 'sg_asset_type','tag_list'])
        print 'asset_info : ', asset_info
        if asset_info:
            if asset_info['sg_asset_type'] in ['chr', 'crd']:
                self.w_publish_file.checkBox_shader.setChecked(True)
            elif asset_info['sg_asset_type']=='prp' and u'交互绑定道具' in asset_info['tag_list']:
                self.w_publish_file.checkBox_shader.setChecked(True)

    def pick_preview_folder(self):
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

        #########################################
        task_folder = self.work_root.replace('\\', '/').replace('/mnt/work/', '/mnt/output/').replace('/task/maya',
                                                                                                      '/output')
        output_folder = task_folder

        c_time = 0
        mov_list = glob.glob(task_folder + '/*/*/*/*/*.mov')
        if mov_list:
            for mov in mov_list:
                if os.stat(mov).st_ctime > c_time or c_time == 0:
                    c_time = os.stat(mov).st_ctime
                    new_mov = mov

            output_folder = os.path.dirname(new_mov)

        pick_dialog.setDirectory(output_folder)
        pick_dialog.setNameFilters(["Images or Video (*.jpg *.jpeg *.tif *.tiff *.mov *.exr)"])
        pick_dialog.exec_()
        l_files = pick_dialog.selectedFiles()

        for file_path in l_files:
            self.w_file.listWidget_preview.addItem(file_path.replace('\\', '/'))

        if self.page_permit < 2:
            self.page_permit = 2
            if self.w_ver.lineEdit_version_name.text() != '.v':
                self.page_permit = 3

    def pick_preview(self):
        # overwrite method of base class, to prompt path picker pointing to nuke task folder, and add checkbox for sequence expanding
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            self.pick_preview_folder()
        else:

            pick_dialog = QtGui.QFileDialog(self)
            pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
            pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

            #########################################
            task_folder = self.work_root.replace('\\', '/').replace('/maya', '/katana') + '/render'
            if os.path.isdir(task_folder):
                pick_dialog.setDirectory(task_folder)
            else:
                pick_dialog.setDirectory(self.work_root.replace('\\', '/').replace('/maya', '/katana'))

            l_files = pick_dialog.getOpenFileNames(filter="Images or Video (*.jpg *.jpeg *.tif *.tiff *.mov *.exr)")

            # if 'PySide' in QtGui.__name__ or 'PyQt5' in QtGui.__name__:
            if QtGui.__name__ in QT_GUI_BASE:
                l_files = l_files[0]

            for file_path in l_files:
                if os.path.exists(file_path):
                    self.w_file.listWidget_preview.addItem(file_path.replace('\\', '/'))

            if self.page_permit < 2:
                self.page_permit = 2
                if self.w_ver.lineEdit_version_name.text() != '.v':
                    self.page_permit = 3
        return
