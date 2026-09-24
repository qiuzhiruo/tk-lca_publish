# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.10
#
# Description: crowd action/animation publish tool.
#
########################################################################################

import os
import sys
import pprint
import shutil
import traceback
import time
import getpass
import pymel.core as pm

import sgtk
from sgtk.platform.qt import QtCore, QtGui
if False:
    from PySide import QtCore, QtGui

from publish_dialog import PublishDialog
from ....ui.dialog import Ui_Dialog
from ....ui.widget_sys import Ui_Form as widget_sys
from ....ui.widget_file import Ui_Form as widget_file
from ....ui.widget_version import Ui_Form as widget_version
from ....ui.widget_check import Ui_Form as widget_check
from ....ui.widget_publish import Ui_Form as widget_publish

from ....ui.widget_file_ani_crowd import Ui_Form as widget_publish_file

import ani.lca_motion_trail.ml_utilities as utils

ACTION_TYPES = ('Still', 'Forward Z', 'Forward', 'Climb', 'Turn', 'Ramp', 'Free')


class AppDialog(PublishDialog):

    def __init__(self, app):

        try:
            PublishDialog.__init__(self, app)

            # Get environment info & production info from sgtk
            self.set_vars()
            self.set_dept_vars(__file__)

            # set up the UI, which includes the dialog and all process widgets
            self.setup_gui(Ui_Dialog, widget_sys, widget_version, widget_file, widget_check, widget_publish, widget_publish_file)

            self.w_file.label_description.setText(u'请设置要提交的行为数据。')

            if False:
                isinstance(self.w_publish_file, widget_publish_file)

            self.w_publish_file.tableWidget_actions.setColumnWidth(0, 120)
            self.w_publish_file.tableWidget_actions.setColumnWidth(1, 80)
            self.w_publish_file.tableWidget_actions.setColumnWidth(2, 80)
            self.w_publish_file.tableWidget_actions.setColumnWidth(3, 200)
            self.w_publish_file.tableWidget_actions.setColumnWidth(4, 80)

            self.w_publish_file.pushButton_add.clicked.connect(self._on_action_add)
            self.w_publish_file.pushButton_remove.clicked.connect(self._on_action_remove)
            self.w_publish_file.pushButton_default.clicked.connect(self._on_action_default)

            self.published_file_type = 'Crowd Action'

            # setup widget functions
            self.do_bind()

            self.show_app_info()
            self._on_action_default()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())

        return

    def setup_tags(self):
        PublishDialog.setup_tags(self)

        # auto set tag
        self.w_sys.comboBox_tag.setCurrentIndex(0)

    def _on_action_add(self, name=None, start=None, end=None, action_type=None, is_cycle=False):
        if name is None:
            name, result = QtGui.QInputDialog.getText(
                self,
                'Add Action',
                'Action Name:',
                text=self.task['name'],
            )
            if not result:
                return

        start, end = utils.frameRange(start, end)

        table = self.w_publish_file.tableWidget_actions
        rows = table.rowCount()
        table.setRowCount(rows+1)

        item = QtGui.QTableWidgetItem()
        item.setData(QtCore.Qt.DisplayRole, name)
        table.setItem(rows, 0, item)

        item = QtGui.QTableWidgetItem()
        item.setData(QtCore.Qt.DisplayRole, start)
        table.setItem(rows, 1, item)

        item = QtGui.QTableWidgetItem()
        item.setData(QtCore.Qt.DisplayRole, end)
        table.setItem(rows, 2, item)

        combo = QtGui.QComboBox()
        combo.addItems(ACTION_TYPES)
        if action_type in ACTION_TYPES:
            index = ACTION_TYPES.index(action_type)
            combo.setCurrentIndex(index)
        table.setCellWidget(rows, 3, combo)

        check = QtGui.QTableWidgetItem()
        check.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        check.setCheckState(QtCore.Qt.Checked if is_cycle else QtCore.Qt.Unchecked)
        table.setItem(rows, 4, check)

    def _on_action_remove(self):
        items = self.w_publish_file.tableWidget_actions.selectedItems()
        rows = []
        for item in items:
            row = item.row()
            if row in rows:
                continue
            rows.append(row)
        rows.sort(reverse=True)
        for row in rows:
            self.w_publish_file.tableWidget_actions.removeRow(row)

    def _on_action_default(self):
        start = pm.playbackOptions( minTime=1, q=1)
        end = pm.playbackOptions( maxTime=1, q=1)

        from production.shotgun_connection import Connection
        sg = Connection('get_project_info').get_sg()
        engine = sgtk.platform.current_engine()
        taskId = engine.context.task['id']
        actionType = sg.find_one('Task', [['id', 'is', taskId]], ['sg_action_type'])['sg_action_type']
        cycle = sg.find_one('Task', [['id', 'is', taskId]], ['sg_remark'])['sg_remark']
        is_cycle = False
        if cycle:
            is_cycle = True

        self.w_publish_file.tableWidget_actions.clearContents()
        self.w_publish_file.tableWidget_actions.setRowCount(0)
        self._on_action_add(name=self.task['name'], start=start, end=end, is_cycle=is_cycle, action_type=actionType)

    def next_page(self):
        current_index = self.ui.stackedWidget.currentIndex()

        # for page 2 and downstream publish
        if current_index == 1 and self.publish_mode == 1:
            table = self.w_publish_file.tableWidget_actions
            self.actions_data = []
            rows = table.rowCount()
            for row in range(rows):
                name = table.item(row, 0).data(QtCore.Qt.DisplayRole)
                start = table.item(row, 1).data(QtCore.Qt.DisplayRole)
                end = table.item(row, 2).data(QtCore.Qt.DisplayRole)
                action_type = table.cellWidget(row, 3).currentIndex()
                is_cycle = table.item(row, 4).checkState() == QtCore.Qt.Checked
                self.actions_data.append(
                    {'name': name,
                     'start': start,
                     'end': end,
                     'action_type': action_type,
                     'is_cycle': is_cycle}
                )
            if self.actions_data:
                self.page_permit = max(self.page_permit, 2)
                if str(self.w_ver.lineEdit_version_name.text()) != '.v':
                    self.page_permit = max(self.page_permit, 3)
            else:
                self.page_permit = 1

        PublishDialog.next_page(self)
