# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.05
#
############################################

import traceback
import pymel.core as pm
import os
import sys
import re

# TODO: is it possible to use relative import here?
sys.path.insert(0, os.path.dirname(__file__) + '/../..')
#import ui
#reload(ui)
from ui.widget_rp_entity import Ui_Form as widget_rp_entity
from ui.dialog_rig_pass import Ui_Dialog as dialog_rig_pass

import ui.dialog_rig_pass as aaa
reload(aaa)

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产的 Rig Pass 是否都设置了属性和值。"
        self.description = u"检查资产的 Rig Pass 是否都设置了属性和值。如果没有需要补上或者跳过。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_rig_passes'])

            self.d_bad_rig_passes = {}
            for rp in asset['sg_rig_passes']:
                rp = self.dialog.sg.find_one('CustomEntity10', [['id', 'is', rp['id']]], ['code', 'sg_attribute', 'sg_value'])
                if rp['sg_attribute'] is None or rp['sg_value'] is None:
                    self.d_bad_rig_passes[rp['code']] = rp

            if len(self.d_bad_rig_passes) > 0:
                return '还没赋值的 rig pass:\n  ' + '\n  '.join(self.d_bad_rig_passes.keys())

            return ""
        except:
            return traceback.format_exc()


    def on_line_edit_change(self):

        return


    def run_fix(self):
        '''Auto Fix'''
        try:
            import sgtk
            from sgtk.platform.qt import QtCore, QtGui

            dlg = QtGui.QDialog(self.dialog)
            rp_dialog = dialog_rig_pass()
            rp_dialog.setupUi(dlg)

            for rp in self.d_bad_rig_passes.keys():
                w = QtGui.QWidget(self.dialog)
                rp_entity = widget_rp_entity()
                rp_entity.setupUi(w)
                rp_entity.label_rp_name.setText(rp)
                self.d_bad_rig_passes[rp]['le_attr'] = rp_entity.lineEdit_rp_attr
                self.d_bad_rig_passes[rp]['le_value'] = rp_entity.lineEdit_rp_value
                rp_dialog.verticalLayout_dlg.addWidget(w)

            dlg.exec_()

            for rp in self.d_bad_rig_passes.values():
                attr = rp['le_attr'].text()
                value = rp['le_value'].text()
                if attr != '' and value != '' and value.isdigit():
                    self.dialog.sg.update('CustomEntity10', rp['id'], {'sg_attribute':attr, 'sg_value': int(value)} )

            return ''
        except:
            return traceback.format_exc()

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



