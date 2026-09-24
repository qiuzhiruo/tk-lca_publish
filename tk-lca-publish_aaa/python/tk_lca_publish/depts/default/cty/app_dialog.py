# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: John Su
#
# Date: 2014.1.2
#
# Description: EFX publish tool.
#
########################################################################################

import os
import traceback

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

    from ....ui.widget_file_cty import Ui_Form as widget_publish_file

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


            self.w_sys.comboBox_tag.setCurrentIndex(1)
            # setup widget functions
            self.do_bind()
            self.do_dept_bind()

            self.show_app_info()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())

        return


    def do_dept_bind(self):
        self.w_publish_file.pushButton_pick_cache.clicked.connect(self.on_pick_cache)
        self.w_publish_file.listWidget_cache.itemClicked.connect(self.remove_cache)
        self.w_publish_file.pushButton_clear_cache.clicked.connect(self.remove_all_cache)

        return


    def on_pick_cache(self):
        pick_dialog = QtGui.QFileDialog(self)

        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.Directory)
        pick_dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, on=True)
        new_root=self.work_root.replace('/task/maya', '')
        new_root=new_root.replace('/mnt/work','/efxcache')
        pick_dialog.setDirectory(new_root)

        res = pick_dialog.exec_()
        if res != QtGui.QDialog.Accepted:
            return
        cache_dir = pick_dialog.selectedFiles()
        self.w_publish_file.listWidget_cache.addItems(cache_dir)
 
        return

    def remove_all_cache(self):
        self.w_publish_file.listWidget_cache.clear()
        
    def remove_cache(self):
        l_items = self.w_publish_file.listWidget_cache.selectedItems()

        if True: #self.w_publish_file.listWidget_cache._mouse_button.name == 'RightButton':
            for item in l_items:
                i = self.w_publish_file.listWidget_cache.indexFromItem(item).row()
                self.w_publish_file.listWidget_cache.takeItem(i)
        return


