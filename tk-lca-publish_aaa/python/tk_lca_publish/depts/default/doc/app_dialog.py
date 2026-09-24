# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: publish tool. 
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

    from ....ui.widget_file_doc import Ui_Form as widget_publish_file

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
            self.lock_publish_mode(v_type='Downstream')

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())
        
        return


    def do_dept_bind(self):
        self.w_publish_file.pushButton_pick_document.clicked.connect(self.on_pick_doc)
        self.w_publish_file.listWidget_document.itemClicked.connect(self.remove_doc)
        return


    def on_pick_doc(self):
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        pick_dialog.setNameFilters(["Document File (*.pdf *.doc *.docx *.txt)", "All Files(*.*)"])
        pick_dialog.exec_()
        l_files = pick_dialog.selectedFiles()

        for file_path in l_files:
            if os.path.isfile(file_path):
                self.w_publish_file.listWidget_document.insertItem(0, file_path.replace('\\', '/'))

        return


    def remove_doc(self):
        l_items = self.w_publish_file.listWidget_document.selectedItems()

        if self.w_publish_file.listWidget_document._mouse_button == QtCore.Qt.RightButton:
            for item in l_items:
                i = self.w_publish_file.listWidget_document.indexFromItem(item).row()
                self.w_publish_file.listWidget_document.takeItem(i)

        return
