# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.05
#
# Description: layout sequence-based publish tool.
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

    import publish_dialog
    reload(publish_dialog)
    from publish_dialog import PublishDialog
    
    from ....ui.dialog import Ui_Dialog
    from ....ui.widget_sys import Ui_Form as widget_sys
    from ....ui.widget_version import Ui_Form as widget_version
    from ....ui.widget_file import Ui_Form as widget_file
    from ....ui.widget_check import Ui_Form as widget_check
    from ....ui.widget_publish import Ui_Form as widget_publish
    from ....ui.widget_file_lay_sequence import Ui_Form as widget_publish_file

    from lay.lca_camera_sequencer import functions
    reload(functions)

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

            self.w_file.groupBox_publish_files.setEnabled(True)
            self.w_file.label_description.setText(u'请选择要提交的镜头和对应的预览文件。')

            self.w_publish_file.tableWidget_shots.setColumnWidth(0, 80)
            self.w_publish_file.tableWidget_shots.setColumnWidth(1, 60)
            self.w_publish_file.tableWidget_shots.setColumnWidth(2, 60)
            self.w_publish_file.tableWidget_shots.setColumnWidth(3, 250)
            self.w_publish_file.tableWidget_shots.setColumnWidth(4, 250)
            self.w_publish_file.tableWidget_shots.itemDoubleClicked.connect(self.on_select_layout_preview)
            self.w_publish_file.tableWidget_shots.itemChanged.connect(self.on_change_check_state)

            # setup widget functions
            self.do_bind()
            self.generate_shot_list()
            
            self.show_app_info()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())

        return

    def set_publish_mode(self):
        PublishDialog.set_publish_mode(self)
        self.w_file.groupBox_publish_files.setEnabled(True)

    def generate_shot_list(self):
        self.shots_raw_data = functions.get_shots()
        scene_path = functions.get_scene_path()
        self.w_publish_file.tableWidget_shots.blockSignals(True)
        self.w_publish_file.tableWidget_shots.setRowCount(len(self.shots_raw_data))
        for i, data in enumerate(self.shots_raw_data):
            _, _, _, _, cut_in, cut_out, shot_info = data
            chck = QtGui.QTableWidgetItem(shot_info['code'])
            chck.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            self.w_publish_file.tableWidget_shots.setItem(i, 0, chck)
            
            item = QtGui.QTableWidgetItem()
            item.setData(QtCore.Qt.DisplayRole, cut_in)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.w_publish_file.tableWidget_shots.setItem(i, 1, item)
            
            item = QtGui.QTableWidgetItem()
            item.setData(QtCore.Qt.DisplayRole, cut_out)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.w_publish_file.tableWidget_shots.setItem(i, 2, item)
            
            default_preview = get_default_preview(scene_path, shot_info)
            item = QtGui.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            item.setData(QtCore.Qt.UserRole, default_preview)
            if os.path.isfile(default_preview):
                item.setData(QtCore.Qt.DisplayRole, default_preview)
                chck.setCheckState(QtCore.Qt.Checked)
            else:
                chck.setCheckState(QtCore.Qt.Unchecked)
            self.w_publish_file.tableWidget_shots.setItem(i, 4, item)
            
            default_topview = get_default_topview(scene_path, shot_info)
            item = QtGui.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            item.setData(QtCore.Qt.UserRole, default_topview)
            if os.path.isfile(default_topview):
                item.setData(QtCore.Qt.DisplayRole, default_topview)
            self.w_publish_file.tableWidget_shots.setItem(i, 5, item)

            other_assets = self.get_other_assets(shot_info['code'])
            if other_assets:
                item = QtGui.QTableWidgetItem(other_assets)
                self.w_publish_file.tableWidget_shots.setItem(i, 3, item)

        
        self.w_publish_file.set_header_check_state()
        self.w_publish_file.tableWidget_shots.blockSignals(False)
    
    def get_other_assets(self,shot_name):
        import maya.cmds as cmds
        import pymel.core as pm
        
        message = None

        cam_ctrl_name = shot_name+'_cam_rig:global_ctrl'
        lca_other_assets_attr = 'LCA_Other_Assets'
        if cmds.objExists(cam_ctrl_name):
            allAttrs = cmds.listAttr(cam_ctrl_name)
            if lca_other_assets_attr not in allAttrs:
                pass
            else:
                message = cmds.getAttr(cam_ctrl_name+'.'+lca_other_assets_attr)
        return message

    def on_select_layout_preview(self, item):
        column_index = item.column()
        if column_index == 4 or column_index == 5:
            target_file = item.data(QtCore.Qt.UserRole)
            default_dir = os.path.dirname(target_file)
            pick_dialog = QtGui.QFileDialog(self)
            pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
            pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
            if column_index == 4:
                pick_dialog.setNameFilter("Preview files (*.mov)")
            elif item.column() == 5:
                pick_dialog.setNameFilter("Topview files (*.mov)")
            
            pick_dialog.setDirectory(default_dir)
            res = pick_dialog.exec_()
            if res == QtGui.QDialog.Accepted:
                target_file = pick_dialog.selectedFiles()[0]
                item.setData(QtCore.Qt.DisplayRole, target_file)
                item.setData(QtCore.Qt.UserRole, target_file)

    def on_change_check_state(self, item):
        if item.column() != 0:
            return

        row = item.row()
        flags = QtCore.Qt.ItemIsEnabled if item.checkState() else QtCore.Qt.NoItemFlags
        for column in range(1, 5):
            item = self.w_publish_file.tableWidget_shots.item(row, column)
            item.setFlags(flags)
    
    def next_page(self):
        current_index = self.ui.stackedWidget.currentIndex()
        if current_index == 1:
            self.shots_preview_data = []
            rows = self.w_publish_file.tableWidget_shots.rowCount()
            for row in range(rows):
                checked = self.w_publish_file.tableWidget_shots.item(row, 0).checkState()
                if not checked:
                    continue
                
                shot_data = self.shots_raw_data[row]
                shot_preview = self.w_publish_file.tableWidget_shots.item(row, 4).data(QtCore.Qt.DisplayRole)
                if not shot_preview:
                    continue
                
                shot_topview = self.w_publish_file.tableWidget_shots.item(row, 5).data(QtCore.Qt.DisplayRole)
                if self.publish_mode != 0:      # if not Daily mode
                    if not shot_topview:
                        continue
                
                self.shots_preview_data.append(
                    {'shot_node': shot_data[0],
                     'camera': shot_data[1],
                     'audio_node': shot_data[2],
                     'overlap': shot_data[3],
                     'cut_in': shot_data[4],
                     'cut_out': shot_data[5],
                     'shot_info': shot_data[6],
                     'preview': shot_preview,
                     'topview': shot_topview
                     }
                )
                # print 'self.shots_preview_data: ', self.shots_preview_data
                
            if self.shots_preview_data:
                self.page_permit = max(self.page_permit, 2)
                if str(self.w_ver.lineEdit_version_name.text()) != '.v':
                    self.page_permit = max(self.page_permit, 3)
            else:
                self.page_permit = 1
            
            if self.w_file.listWidget_preview.count() == 0:
                self.page_permit = 1

        PublishDialog.next_page(self)
        


def get_default_preview(scene_path, shot_info):
    return get_default_mov(scene_path, shot_info, 'data')

def get_default_topview(scene_path, shot_info):
    return get_default_mov(scene_path, shot_info, 'topview')

def get_default_mov(scene_path, shot_info, mov_dir):
    """
    shot_info, e.g. {u'sg_cut_in': 1001, u'code': u'd60230', u'sg_sequence': {u'type': u'Sequence', u'id': 107, u'name': u'd60'}, u'sg_cut_out': 1042, u'type': u'Shot', u'id': 7910}
    """
    shot_file = functions.seq_to_shot_work(scene_path, shot_info)
    dirname, filename = os.path.split(shot_file)
    return os.path.join(dirname, mov_dir, filename[:-3] + '.mov')


