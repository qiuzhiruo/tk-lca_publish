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

from ....ui.widget_file_hyperloop import Ui_Form as widget_publish_file


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

            #self.image_layout=self.w_publish_file.layout_image.ThexShowImageWidgetFlowLayout
            self.no_version_image_list=[]

            # setup widget functions
            self.do_bind()

            self.show_app_info()

            self.lock_publish_mode(v_type='Downstream')
            self.w_file.listWidget_preview.addItem(os.path.dirname(__file__) + '/hyperloop_logo.jpg')

            self.w_publish_file.pushButton_xml.clicked.connect(self.on_pick_xml)
            
            self.get_assets()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            self._app.log_error(traceback.format_exc())
        
        return


    def pick_file(self, root, extension):
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        pick_dialog.setDirectory(root)
        dir_filter = QtCore.QDir()
        dir_filter.setFilter(QtCore.QDir.AllDirs|QtCore.QDir.Files)
        dir_filter.setNameFilters((extension))
        pick_dialog.setFilter(extension)
        pick_dialog.exec_()

        return pick_dialog.selectedFiles()


    def get_assets(self):
        self.d_assets = {}
        for asset in self.sg.find('Asset', [['project', 'is', self.project], ['sg_status_list', 'is_not', 'omt']], ['sg_asset_type', 'code', 'sg_chinese']):
            if not asset['sg_asset_type'] in ['prp', 'env', 'asb']:
                continue

            if asset['code'] is None :
                continue

            if asset['sg_chinese'] is None:
                asset['sg_chinese'] = ''

            self.d_assets[asset['code']] = asset
        return

    
    def on_pick_xml(self):
        for file_path in self.pick_file(self.work_root, "*.xml"):
            file_path_str=str(file_path)
            self.w_publish_file.lineEdit_xml.setText(file_path)
        return 

