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

    from ....ui.widget_file_cfx_shot import Ui_Form as widget_publish_file

except:
    print traceback.format_exc()

TXT_DEFAULT = QtGui.QColor(200, 200, 200)
TXT_ORANGE = QtGui.QColor(255, 150, 30)
TXT_RED = QtGui.QColor(255, 50, 50)
TXT_BLUE = QtGui.QColor(150, 150, 255)
TXT_WHITE = QtGui.QColor(255, 255, 255)


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
        return


    def on_pick_cache(self):
        if self.publish_mode == 0:
            self.print_log('Daily Publish need not pick cache!\n', txt_color = TXT_ORANGE)
            return

        pick_dialog = QtGui.QFileDialog(self)
      
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.Directory)
        pick_dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, on=True)
        pick_dialog.setDirectory(self.output_root)

        try:
            proxy_model = FolderFilterProxyModel(pick_dialog)
            proxy_model.setSearchText(str(self.version_key))
            pick_dialog.setProxyModel(proxy_model)
        except:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())

        pick_dialog.exec_()
        
        cache_dir = pick_dialog.selectedFiles()[0].replace('\\', '/')
        
        if os.path.isdir(cache_dir):
            self.w_publish_file.listWidget_cache.insertItem(0, cache_dir)
            
            #tokens = cache_dir.split('/')[-1].split('.')
            tokens = cache_dir.split('/')
            if 'cfx' in tokens:
                i = tokens.index('cfx')
                if len(tokens) > i+2:
                    v_tokens = tokens[i+2].split('.')
                    if len(v_tokens[-1]) ==4 and v_tokens[-1][0] == 'v' and v_tokens[-1][1:].isdigit():
                        self.w_ver.lineEdit_version_name.setText('.'+v_tokens[-1])

        return


    def remove_cache(self):
        l_items = self.w_publish_file.listWidget_cache.selectedItems()

        if True: #self.w_publish_file.listWidget_cache._mouse_button.name == 'RightButton':
            for item in l_items:
                i = self.w_publish_file.listWidget_cache.indexFromItem(item).row()
                self.w_publish_file.listWidget_cache.takeItem(i)
        return


class FolderFilterProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FolderFilterProxyModel, self).__init__(parent)
        self.searchText=None

    def setSearchText(self, arg=None):
        self.searchText=arg

    def filterAcceptsRow(self, source_row, srcidx):
        model = self.sourceModel()
        index0 = model.index(source_row, 0, srcidx)
        index1 = model.index(source_row, 1, srcidx)
        index2 = model.index(source_row, 2, srcidx)

        str2_filenamerole = model.data(index2, QtGui.QFileSystemModel.FileNameRole)
        str2_displayrole = model.data(index2, QtCore.Qt.DisplayRole)

        if str2_displayrole in ('Folder', 'Drive') and '.' not in str2_filenamerole: 
            return True
        
        if self.searchText in str2_filenamerole:
            return True
        else:
            return False