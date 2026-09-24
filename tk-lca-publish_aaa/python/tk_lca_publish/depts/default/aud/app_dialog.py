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
import re
import subprocess
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

from ....ui.widget_file_audio import Ui_Form as widget_publish_file



def ensure_browse_x_permission(path):
    """
    仅用于 UI 浏览：
    - 给路径链路补 x 权限
    - 不给 w
    """

    cmd = 'su -'
    root_cmd = '''chmod a+rx -R %s''' % path
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.stdin.write('20150312')
    p.stdin.write('\n')
    out, err = p.communicate(root_cmd)
    if err is None:
        # print('change chmod ok')
        return True
    else:
        # print ('change chmod error')
        return False

def path_change_chmod(path):
    """
    解路径权限
    """
    cmd = 'su -'
    root_cmd = '''chmod 777 -R %s''' % path
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.stdin.write('20150312')
    p.stdin.write('\n')
    out, err = p.communicate(root_cmd)
    if err is None:
        # print('change chmod ok')
        return True
    else:
        # print ('change chmod error')
        return False


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

            # 根据项目名决定是否默认勾选 Add Wave Length
            self.set_add_wave_length_default()

            self.show_app_info()

            self.is_add_wave_length = False

            self.lock_publish_mode(v_type='Downstream')

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            self._app.log_error(traceback.format_exc())
        
        return

    def do_dept_bind(self):
        self.w_publish_file.pushButton_pick_wav.clicked.connect(self.on_pick_wav)
        self.w_publish_file.pushButton_clear_wav.clicked.connect(self.on_clear_wav)
        self.w_publish_file.xml_file_btn.clicked.connect(self.on_xmlFile_clicked)
        self.w_publish_file.seq_checkbox.stateChanged.connect(self.on_seqCheckBox_stateChanged)

        self.w_publish_file.add_wave_length_checkbox.stateChanged.connect(self.on_addWaveLengthCheckBox_stateChanged)

        # 添加互斥逻辑：监听文本变化
        self.w_publish_file.exclusive_lineEdit.textChanged.connect(self.on_exclusive_textChanged)
        self.w_publish_file.inclusive_lineEdit.textChanged.connect(self.on_inclusive_textChanged)
        return

    def on_exclusive_textChanged(self, text):
        """
        当"不需更新的镜头号"有内容时，禁用"只更新的镜头号"
        """
        if text.strip():  # 如果有内容
            self.w_publish_file.inclusive_lineEdit.setEnabled(False)
            self.w_publish_file.inclusive_label.setEnabled(False)
        else:  # 如果为空
            # 恢复启用状态（如果 seq_checkbox 是选中的）
            if self.w_publish_file.seq_checkbox.isChecked():
                self.w_publish_file.inclusive_lineEdit.setEnabled(True)
                self.w_publish_file.inclusive_label.setEnabled(True)

    def on_inclusive_textChanged(self, text):
        """
        当"只更新的镜头号"有内容时，禁用"不需更新的镜头号"
        """
        if text.strip():  # 如果有内容
            self.w_publish_file.exclusive_lineEdit.setEnabled(False)
            self.w_publish_file.exclusive_label.setEnabled(False)
        else:  # 如果为空
            # 恢复启用状态（如果 seq_checkbox 是选中的）
            if self.w_publish_file.seq_checkbox.isChecked():
                self.w_publish_file.exclusive_lineEdit.setEnabled(True)
                self.w_publish_file.exclusive_label.setEnabled(True)

    def set_add_wave_length_default(self):
        """
        根据项目名决定是否默认勾选 Add Wave Length checkbox。
        用户可在此方法中配置哪些项目需要默认开启。
        """
        # 需要默认开启 add_wave_length 的项目名列表
        ADD_WAVE_LENGTH_PROJECTS = []  # 用户自行填写项目名，如 ['YZC', 'LRS']

        proj_name = self.project['name'].upper()
        if proj_name in ADD_WAVE_LENGTH_PROJECTS:
            self.w_publish_file.add_wave_length_checkbox.setChecked(True)
            self.is_add_wave_length = True
        else:
            self.is_add_wave_length = False

    def on_addWaveLengthCheckBox_stateChanged(self, state):
        self.is_add_wave_length = bool(state)


    def on_pick_wav(self):
        self.print_log(QtGui.__file__)
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

        browse_root = self.work_root.replace('/maya', '/final_cut')
        ensure_browse_x_permission(browse_root)


        pick_dialog.setDirectory(browse_root)
        pick_dialog.setLabelText(QtGui.QFileDialog.Accept, '&Select')
        pick_dialog.setNameFilters(["Wav File (*.wav)"])
        pick_dialog.exec_()

        # 用户选中的 wav 文件
        l_files = pick_dialog.selectedFiles()

        # =========================
        # 自动解权限：路径白名单
        # =========================
        FINAL_CUT_WHITELIST = re.compile(
            r'^/mnt/work/projects/[^/]+/preproduction/[^/]+/story/(aud|edt)/task/final_cut($|/)'
        )

        unlocked_dirs = set()

        for f in l_files:
            parent_dir = os.path.dirname(f)
            parent_dir = os.path.normpath(parent_dir).replace('\\', '/')

            # shots / 子目录 → 回退到 final_cut 层判断
            check_dir = parent_dir
            while check_dir and check_dir != '/':
                if check_dir.endswith('/final_cut'):
                    break
                check_dir = os.path.dirname(check_dir)

            # 不在 final_cut 体系内，直接跳过
            if not check_dir or not FINAL_CUT_WHITELIST.match(check_dir):
                continue

            # 同一个目录只解一次
            if parent_dir in unlocked_dirs:
                continue

            try:
                path_change_chmod(parent_dir)
                # 可选：只打 log，不弹窗
                # write_chmod_log(getpass.getuser(), parent_dir, 'AUTO_UNLOCK_WAV_DIR')
            except Exception:
                print(traceback.format_exc())

            unlocked_dirs.add(parent_dir)

        # =========================
        # 原有逻辑：按文件名去重
        # =========================
        wav_files = []
        for i in range(self.w_publish_file.listWidget_wavfiles.count()):
            file_txt = str(self.w_publish_file.listWidget_wavfiles.item(i).text())
            wav_files.append(os.path.basename(file_txt))

        for f in l_files:
            if os.path.basename(f) not in wav_files:
                self.w_publish_file.listWidget_wavfiles.addItem(f)

        return

    def on_clear_wav(self):
        sel_items=self.w_publish_file.listWidget_wavfiles.selectedItems()
        for s in sel_items:
            self.w_publish_file.listWidget_wavfiles.takeItem(self.w_publish_file.listWidget_wavfiles.row(s))

        return

    def on_xmlFile_clicked(self):
        """
        """
        xml_file_dialog = QtGui.QFileDialog(self)
        xml_file_dialog.setViewMode(QtGui.QFileDialog.Detail)
        xml_file_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        xml_file_dialog.setDirectory(self.work_root.replace('/maya', '/final_cut'))
        xml_file_dialog.setLabelText(QtGui.QFileDialog.Accept,'&Select')
        xml_file_dialog.setNameFilters(["XML/AAF (*.xml *.aaf)", "All Files(*.*)"])
        xml_file_dialog.exec_()
    
        xml_file = xml_file_dialog.selectedFiles()[0]
    
        if os.path.isfile(xml_file):
            self.w_publish_file.xml_lineEdit.setText(xml_file)
        
    
    def on_seqCheckBox_stateChanged(self, state):
        """
        """
        if self.w_publish_file.seq_checkbox.isChecked() :
            self.w_publish_file.exclusive_lineEdit.setEnabled(True)
            self.w_publish_file.exclusive_label.setEnabled(True)

            self.w_publish_file.inclusive_lineEdit.setEnabled(True)
            self.w_publish_file.inclusive_label.setEnabled(True)
        else:
            self.w_publish_file.exclusive_lineEdit.setEnabled(False)
            self.w_publish_file.exclusive_label.setEnabled(False)

            self.w_publish_file.inclusive_lineEdit.setEnabled(False)
            self.w_publish_file.inclusive_label.setEnabled(False)