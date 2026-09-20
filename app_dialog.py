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
import re

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

    from ....ui.widget_file_plt_sg import Ui_Form as widget_publish_file

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
            # self.w_file.thumbnail_widget.setEnabled(False)

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
        self.w_publish_file.pushButton_pick_cache.clicked.connect(self.on_pick_cache)

    def on_pick_cache(self):
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.Directory)
        pick_dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, on=True)

        output_path=self.work_root.replace('/task/maya', '/output/')
        output_path=output_path.replace('/mnt/work','/output')
        pick_dialog.setDirectory(output_path)

        res = pick_dialog.exec_()

        if res != QtGui.QDialog.Accepted:
            return

        output_version_dir = str(pick_dialog.selectedFiles()[0])
        if os.path.isdir(output_version_dir) and \
            re.match('\S+/plt/output/\S+\.v\d{3}',output_version_dir) and \
            os.path.isdir(output_version_dir+'/cache'):
            self.w_publish_file.lineEdit_cache.setText(output_version_dir.replace('\\', '/'))
