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

from ....ui.widget_file_art_shot import Ui_Form as widget_publish_file
from ....ui.widget_file_art_shot import ui_ThxWidgetItem as ui_ThxWidgetItem


class AppDialog(PublishDialog):

    def __init__(self, app):

        try:
            PublishDialog.__init__(self, app)

            # Get environment info & production info from sgtk
            self.set_vars()
            self.set_dept_vars( __file__ )
            # set up the UI, which includes the dialog and all process widgets           
            self.setup_gui(Ui_Dialog, widget_sys, widget_version, widget_file, widget_check, widget_publish, widget_publish_file)
            self.ui_ThxWidgetItem=ui_ThxWidgetItem
            # TODO Can't use the thumbnail widget outside Maya
            self.w_file.thumbnail_widget.setEnabled(False)

            self.image_layout=self.w_publish_file.layout_image.ThexShowImageWidgetFlowLayout
            self.no_version_image_list=[]

            # setup widget functions
            self.do_bind()

            self.show_app_info()

            self.lock_publish_mode(v_type='Daily')
            self.w_publish_file.delete_button.clicked.connect(self.get_invisible_image)
            self.init_seq_link()


        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            self._app.log_error(traceback.format_exc())
        
        return

    def get_invisible_image(self):
        l_preview_files = [self.w_file.listWidget_preview.item(i).text() for i in xrange(self.w_file.listWidget_preview.count())]

        if len(l_preview_files) == 0:
            # if sys.platform.startswith('win'):
            #     self.w_file.listWidget_preview.addItem('U:/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/depts/default/art/delete_image.jpg')
            # else:
            #     self.w_file.listWidget_preview.addItem('/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/depts/default/art/delete_image.jpg')
            tk_lca_publish_path = os.path.join(os.environ['LC_UTILITY'], '/lca_sgtk_apps/tk-lca-publish').replace('\\', '/')
            self.w_file.listWidget_preview.addItem('{}/python/tk_lca_publish/depts/default/art/delete_image.jpg'.format(tk_lca_publish_path))
            self.page_permit = 2




    def init_seq_link(self):
        self.Seq_TableWidget = self.w_publish_file.layout_image.Seq_TableWidget
        seq_list=[]
        Asset=self.sg.find_one('Asset', [['id', 'is', self.entity['id']]], ['sequences'])

        if Asset and Asset.has_key('sequences'):
            seq_list=[seq['name'] for seq in Asset['sequences']]

        self.Seq_TableWidget.setRowCount(len(seq_list))

        for i,seq in enumerate(seq_list):

            seq_item=QtGui.QTableWidgetItem(seq)
            seq_item.setCheckState(QtCore.Qt.CheckState())
            self.Seq_TableWidget.setItem(i,0,seq_item)
