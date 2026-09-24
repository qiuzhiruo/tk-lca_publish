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
import traceback

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

    from ....ui.widget_file_srf_asb import Ui_Form as widget_publish_file

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
            self.do_dept_bind()

            self.show_app_info()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            self._app.log_error(traceback.format_exc())
        
        return



    def do_dept_bind(self):
        self.w_publish_file.pushButton_pick_srf.clicked.connect(self.on_pick_srf)
        return


    def on_pick_srf(self):

        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        pick_dialog.setDirectory(self.work_root.replace('/maya', '/katana'))
        pick_dialog.setNameFilters(["Srf Config File (*.srf)"])

        if pick_dialog.exec_():
            l_files = pick_dialog.selectedFiles()
            l_files_str=';'.join([str(l) for l in l_files])
            self.w_publish_file.lineEdit_srf.setText(str(l_files_str))

    def pick_preview(self):
        # overwrite method of base class, to prompt path picker pointing to nuke task folder, and add checkbox for sequence expanding
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

        #########################################
        task_folder = self.work_root.replace('\\', '/').replace('/maya', '/katana') + '/render'
        if os.path.isdir( task_folder ):
            pick_dialog.setDirectory( task_folder )
        else:
            pick_dialog.setDirectory( self.work_root.replace('\\', '/').replace('/maya', '/katana') )

        pick_dialog.setNameFilters(["Images or Video (*.jpg *.jpeg *.tif *.tiff *.mov *.exr)"])
        pick_dialog.exec_()
        l_files = pick_dialog.selectedFiles()

        for file_path in l_files:
            self.w_file.listWidget_preview.addItem(file_path.replace('\\', '/'))

        if self.page_permit < 2:
            self.page_permit = 2
            if self.w_ver.lineEdit_version_name.text() != '.v':
                self.page_permit = 3
        return
