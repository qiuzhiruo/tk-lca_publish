# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.02
#
# Description: Publish tool. Create version on server and shtogun
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
import re

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

    from ....ui.widget_file_lgt import Ui_Form as widget_publish_file

except:
    print traceback.format_exc()

import production.pipeline.utils as pplu


class AppDialog(PublishDialog):

    def __init__(self, app):

        try:
            PublishDialog.__init__(self, app)

            # Get environment info & production info from sgtk
            self.set_vars()
            self.set_dept_vars( __file__ )

            # set up the UI, which includes the dialog and all process widgets            
            self.setup_gui(Ui_Dialog, widget_sys, widget_version, widget_file, widget_check, widget_publish, widget_publish_file)

            # TODO Can't use the thumbnail widget outside Maya
            self.w_file.thumbnail_widget.setEnabled(False)

            # setup widget functions
            self.do_bind()
            self.do_dept_bind()
            self.show_app_info()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            self._app.log_error(traceback.format_exc())
        
        return

    def get_auto_description(self,nk_file):
        all_version=[]
        with open(nk_file) as f:
            for l in f.readlines():
                lgt_finder=re.findall('/lgt/output/nuke/R1/v(\d{3})/', l)
                if lgt_finder: all_version.append(lgt_finder[0])
                else:
                    lgt_finder=re.findall('/lgt/publish/[a-z]\d{5}\.lgt\.lighting\.v(\d{3})/', l)
                    if lgt_finder: all_version.append(lgt_finder[0])
                    
        if all_version:
            return 'lgt version: v'+sorted(all_version)[-1]

    def do_dept_bind(self):
        self.w_publish_file.pushButton_lseq.clicked.connect(self.on_pick_l)
        self.w_publish_file.pushButton_rseq.clicked.connect(self.on_pick_r)
        self.w_publish_file.pushButton_nk.clicked.connect(self.on_pick_nk)
        self.w_publish_file.lineEdit_lseq.textChanged.connect(self.lseq_changed)
        return

    def lseq_changed(self):
        lseq_txt=str(self.w_publish_file.lineEdit_lseq.text())
        if os.path.isdir(lseq_txt):
            self.w_publish_file.lineEdit_rseq.setEnabled(True)
            self.w_publish_file.pushButton_rseq.setEnabled(True)
        else:
            self.w_publish_file.lineEdit_rseq.setEnabled(False)
            self.w_publish_file.pushButton_rseq.setEnabled(False)

    def on_pick_l(self):
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.Directory)
        pick_dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, on=True)
        output_path=self.work_root.replace('/task/maya', '/output')
        output_path=output_path.replace('/mnt/work','/output')
        pick_dialog.setDirectory(output_path)
        res = pick_dialog.exec_()

        if res != QtGui.QDialog.Accepted:
            return

        render_dir = str(pick_dialog.selectedFiles()[0])
        if os.path.isdir(render_dir):
            exr_dir=render_dir.replace('\\', '/')
            try:
                version_tag=exr_dir.split('/')[-2]
                self.w_ver.lineEdit_version_name.setText('.'+version_tag)
            except:
                pass

            self.w_publish_file.lineEdit_lseq.setText(exr_dir)
            self.lseq_changed()

            exrs=pplu.findFiles(exr_dir,'.exr')
            if not exrs:
                exrs=pplu.findFiles(exr_dir,'.jpg')
            self.w_file.listWidget_preview.clear()
            for s in exrs:
                self.w_file.listWidget_preview.addItem(s)
            try:
                self.page_permit = 3
                if exr_dir.endswith('L'):
                    r_guess=os.path.join(os.path.dirname(exr_dir),'R')
                    if os.path.isdir(r_guess) and os.listdir(r_guess):
                        self.w_publish_file.lineEdit_rseq.setText(r_guess)
            except:
                self.print_log(traceback.format_exc())

            try:
                work_shot=render_dir.replace('/output/projects/', '/mnt/work/projects/').replace('/output/nuke/', '/task/nuke/').rsplit('/',3)[0]
                version_num=render_dir.split('/')[-2]
                nuke_file=work_shot+'/'+self.entity['name']+'.'+self.step['name']+{'lgt':'.comp.','pfx':'.paint_fix.'}[self.step['name']]+version_num+'.nk'
                self.print_log(nuke_file)
                if os.path.isfile(nuke_file):
                    self.w_publish_file.lineEdit_nk.setText(nuke_file.replace('\\', '/'))
            except:
                self.print_log(traceback.format_exc())

        return

    def on_pick_r(self):
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.Directory)
        pick_dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, on=True)
        output_path=self.work_root.replace('/task/maya', '/output')
        output_path=output_path.replace('/mnt/work','/output')
        pick_dialog.setDirectory(output_path)
        res = pick_dialog.exec_()

        if res != QtGui.QDialog.Accepted:
            return

        render_dir = str(pick_dialog.selectedFiles()[0])
        if os.path.isdir(render_dir):
            self.w_publish_file.lineEdit_rseq.setText(render_dir.replace('\\', '/'))

        return

    def on_pick_nk(self):
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        pick_dialog.setNameFilters(["Srf Config File (*.nk)"])
        output_path=self.work_root.replace('/task/maya', '/task/nuke')
        pick_dialog.setDirectory(output_path)

        res = pick_dialog.exec_()

        if res != QtGui.QDialog.Accepted:
            return

        render_dir = str(pick_dialog.selectedFiles()[0])
        if os.path.isfile(render_dir):
            nk_file=render_dir.replace('\\', '/')
            self.w_publish_file.lineEdit_nk.setText(nk_file)
            lgt_version=self.get_auto_description(nk_file)
            if lgt_version:
                self.w_publish.plainTextEdit_auto_description.setPlainText(lgt_version)
        return
