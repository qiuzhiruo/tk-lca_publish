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

    from ....ui.widget_file_picture_lock import Ui_Form as widget_publish_file

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

            # TODO Can't use the thumbnail widget outside Maya
            self.w_file.thumbnail_widget.setEnabled(False)

            # setup widget functions
            self.do_bind()
            self.w_publish_file.pushButton_edt.clicked.connect(self.on_pick_edt)
            self.w_publish_file.pushButton_audio.clicked.connect(self.on_pick_audio)

            self.show_app_info()

            self.lock_publish_mode(v_type='Downstream')

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            self._app.log_error(traceback.format_exc())
 
    def on_pick_edt(self):
        #edt_file = QtGui.QFileDialog.getOpenFileName(self, "Pick a edt cut file", self.work_root, "Edt Cut File(*.txt)")[0]
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        pick_dialog.setDirectory(self.work_root)
        pick_dialog.setLabelText(QtGui.QFileDialog.Accept,'&Select')
        pick_dialog.setNameFilters(["Txt File (*.txt)"])
        pick_dialog.exec_()

        edt_file = pick_dialog.selectedFiles()[0]

        if os.path.isfile(edt_file):
            self.w_publish_file.lineEdit_edt.setText(edt_file)
        return

    def on_pick_audio(self):
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        pick_dialog.setDirectory(self.work_root)
        pick_dialog.setLabelText(QtGui.QFileDialog.Accept,'&Select')
        pick_dialog.setNameFilters(["Audio File (*.wav)"])
        pick_dialog.exec_()

        aud_file = pick_dialog.selectedFiles()[0]

        if os.path.isfile(aud_file):
            self.w_publish_file.lineEdit_audio.setText(aud_file)
        return

