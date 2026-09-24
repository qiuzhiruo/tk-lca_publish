# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: John Su
#
# Date: 2014.1.2
#
# Description: CFX publish tool. 
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
    from ....ui.widget_version import Ui_Form as widget_version
    from ....ui.widget_file import Ui_Form as widget_file
    from ....ui.widget_check import Ui_Form as widget_check
    from ....ui.widget_publish import Ui_Form as widget_publish

    from ....ui.widget_file_plt_shot import Ui_Form as widget_publish_file
    reload(widget_publish_file)
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
            self.setup_gui(Ui_Dialog, widget_sys, widget_version, widget_file, widget_check, widget_publish, widget_publish_file)

            # setup widget functions
            self.do_bind()
            # self.do_dept_bind()

            self.show_app_info()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())
        
        return


    # def do_dept_bind(self):
    #     self.w_publish_file.pushButton_pick_cache.clicked.connect(self.on_pick_cache)
    #     self.w_publish_file.listWidget_cache.itemClicked.connect(self.remove_cache)
    #     return


    # def on_pick_cache(self):
    #     pick_dialog = QtGui.QFileDialog(self)
      
    #     pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
    #     pick_dialog.setFileMode(QtGui.QFileDialog.Directory)
    #     #pick_dialog.setFileMode(QtGui.QFileDialog.ShowDirsOnly)
    #     pick_dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, on=True)
    #     pick_dialog.setDirectory(self.output_root)
    #     pick_dialog.exec_()
        
    #     cache_dir = pick_dialog.selectedFiles()[0].replace('\\', '/')
        
    #     if os.path.isdir(cache_dir):
    #         self.w_publish_file.listWidget_cache.insertItem(0, cache_dir)
            
    #         #tokens = cache_dir.split('/')[-1].split('.')
    #         tokens = cache_dir.split('/')
    #         if 'plt' in tokens:
    #             i = tokens.index('plt')
    #             if len(tokens) > i+2:
    #                 v_tokens = tokens[i+2].split('.')
    #                 if len(v_tokens[-1]) ==4 and v_tokens[-1][0] == 'v' and v_tokens[-1][1:].isdigit():
    #                     self.w_ver.lineEdit_version_name.setText('.'+v_tokens[-1])

    #     return


    # def remove_cache(self):
    #     l_items = self.w_publish_file.listWidget_cache.selectedItems()

    #     if True: #self.w_publish_file.listWidget_cache._mouse_button.name == 'RightButton':
    #         for item in l_items:
    #             i = self.w_publish_file.listWidget_cache.indexFromItem(item).row()
    #             self.w_publish_file.listWidget_cache.takeItem(i)
    #     return



