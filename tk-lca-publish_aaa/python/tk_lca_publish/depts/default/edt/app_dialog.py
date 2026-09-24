# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.01
#
# Description: 
#
########################################################################################

import os
import sys
import re
import pprint
import subprocess
import shutil
import traceback
import time

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

    from ....ui.widget_file_edt import Ui_Form as widget_publish_file

except:
    print traceback.format_exc()


def split_line(line):
    line = line.replace('\n', ' ')
    line = line.replace('\r', ' ')
    tokens = line[:-1].split(' ')
    t2 = []
    for token in tokens:
        if token != '':
            t2.append(token)

    return t2

def convert_frames(time):
    t = time.split(':')
    f = int(t[3]) + 24*int(t[2]) + 1440*int(t[1]) + 86400*int(t[0])
    return f


class AppDialog(PublishDialog):

    FINAL_CUT_WHITELIST = re.compile(
        r'^/mnt/work/projects/[^/]+/preproduction/[^/]+/story/(aud|edt)/task/final_cut($|/)'
    )

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

            # Adjust gui
            self.w_publish_file.tableWidget_shots.setColumnWidth(0, 80)
            self.w_publish_file.tableWidget_shots.setColumnWidth(1, 80)
            self.w_publish_file.tableWidget_shots.setColumnWidth(2, 80)
            self.w_publish_file.tableWidget_shots.setColumnWidth(3, 90)
            self.w_publish_file.tableWidget_shots.setColumnWidth(4, 110)
            self.w_publish_file.tableWidget_shots.setColumnWidth(5, 200)

            self.show_app_info()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            self._app.log_error(traceback.format_exc())
        
        return

    def _run_root_cmd(self, root_cmd):
        cmd = 'su -'
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.stdin.write('20150312')
        p.stdin.write('\n')
        out, err = p.communicate(root_cmd)
        return err is None

    def _ensure_browse_x_permission(self, path):
        """
        仅用于 UI 浏览：
        - 给路径链路补 x 权限
        - 不给 w
        """
        if not path:
            return False

        root_cmd = '''chmod a+rx -R %s''' % path
        return self._run_root_cmd(root_cmd)

    def _path_change_chmod(self, path):
        """
        解路径权限
        """
        if not path:
            return False

        root_cmd = '''chmod 777 -R %s''' % path
        return self._run_root_cmd(root_cmd)

    def _get_final_cut_browse_root(self):
        return self.work_root.replace('/maya', '/final_cut')

    def _prepare_final_cut_browse(self):
        browse_root = self._get_final_cut_browse_root()
        self._ensure_browse_x_permission(browse_root)
        return browse_root

    def _unlock_selected_final_cut_dirs(self, l_files):
        unlocked_dirs = set()

        for file_path in l_files:
            parent_dir = os.path.dirname(str(file_path))
            parent_dir = os.path.normpath(parent_dir).replace('\\', '/')

            check_dir = parent_dir
            while check_dir and check_dir != '/':
                if check_dir.endswith('/final_cut'):
                    break
                check_dir = os.path.dirname(check_dir)

            if not check_dir or not self.FINAL_CUT_WHITELIST.match(check_dir):
                continue

            if parent_dir in unlocked_dirs:
                continue

            try:
                self._path_change_chmod(parent_dir)
            except Exception:
                print(traceback.format_exc())

            unlocked_dirs.add(parent_dir)

        return unlocked_dirs


    def do_dept_bind(self):
        self.w_publish_file.pushButton_pick_edl.clicked.connect(self.on_pick_edl)
        self.w_publish_file.pushButton_reload.clicked.connect(self.on_load)
        return


    def on_load(self):
        edl_file = str(self.w_publish_file.lineEdit_edl.text())
        if not os.path.isfile(edl_file):
            return

        self.w_publish_file.tableWidget_shots.setRowCount(0)

        # diagnostic the edl file
        f = open( edl_file, 'r')
        contents = f.readlines()
        f.close()

        d_edt_shots = {}
        for i in range(len( contents) - 1):
            line = contents[i]
            tokens_a = split_line(line)
            if len(tokens_a) == 0:
                continue

            if tokens_a[0].isdigit():
                tokens_b = split_line(contents[i+1])
                if tokens_b[0] == tokens_a[0]:
                    tokens_b = split_line(contents[i+2])

                if tokens_b[-1].endswith('.MOV') and 'V' in tokens_a[2]:
                    f1 = convert_frames(tokens_a[-4])
                    f2 = convert_frames(tokens_a[-3])

                    if f1 != f2:
                        #print tokens_a[0], tokens_b[-1], f1, f2, tokens_a[-4:]
                        shot_name = tokens_b[-1].split('.')[0].lower()
                        if not d_edt_shots.has_key(shot_name):
                            d_edt_shots[shot_name] = {'edl_fstart':99999999, 'edl_fend':-99999999, 'mov':tokens_b[-1]}

                        if f1 < d_edt_shots[shot_name]['edl_fstart']:
                            d_edt_shots[shot_name]['edl_fstart'] = f1

                        if f2 > d_edt_shots[shot_name]['edl_fend']:
                            d_edt_shots[shot_name]['edl_fend'] = f2-1

        #self.w_publish_file.tableWidget_shots.setRowCount(len(d_edt_shots.keys()))
        #QtGui.QMessageBox.about(self, "1", u"1。")

        l_seq_shots = self.sg.find('Shot',[['sg_status_list', 'is_not', 'omt'], ['sg_sequence', 'is', self.entity]], ['code', 'sg_cut_in', 'sg_cut_out', 'sg_cut_duration'])

        self.w_publish_file.tableWidget_shots.setRowCount(len(l_seq_shots))

        self.d_seq_shots = {}
        for shot in l_seq_shots:
            self.d_seq_shots[shot['code']] = shot

        l_shots = sorted(self.d_seq_shots.keys())
        for i in range(len(l_shots)):
            self.w_publish_file.tableWidget_shots.setRowHeight(i, 25)
            shot_name = l_shots[i]
            shot_item = QtGui.QTableWidgetItem(shot_name)
            self.w_publish_file.tableWidget_shots.setItem(i, 0, shot_item)

            sg_cut_in = self.d_seq_shots[shot_name]['sg_cut_in']
            sg_cut_out = self.d_seq_shots[shot_name]['sg_cut_out']
            sg_cut_duration = self.d_seq_shots[shot_name]['sg_cut_duration']

            if sg_cut_in :
                newItem = QtGui.QTableWidgetItem( str(sg_cut_in) )
                self.w_publish_file.tableWidget_shots.setItem(i, 1, newItem)

            if sg_cut_out :
                newItem = QtGui.QTableWidgetItem( str(sg_cut_out) )
                self.w_publish_file.tableWidget_shots.setItem(i, 2, newItem)
                
            if sg_cut_duration:
                newItem = QtGui.QTableWidgetItem(str(sg_cut_duration))
                self.w_publish_file.tableWidget_shots.setItem(i, 3, newItem)

            if d_edt_shots.has_key(shot_name):
                edl_cut_in =  d_edt_shots[shot_name]['edl_fstart']
                edl_cut_out = d_edt_shots[shot_name]['edl_fend']
                if sg_cut_in and edl_cut_in < 100:
                    edl_cut_in =  sg_cut_in + d_edt_shots[shot_name]['edl_fstart']
                    edl_cut_out =  sg_cut_in + d_edt_shots[shot_name]['edl_fend']
                
                edl_cut_duration = edl_cut_out - edl_cut_in + 1
                edl_duration_item = QtGui.QTableWidgetItem(str(edl_cut_duration))
                if sg_cut_duration != edl_cut_duration:
                    edl_duration_item.setBackground( QtGui.QBrush(QtGui.QColor(255, 50, 50)))
                    shot_item.setBackground( QtGui.QBrush(QtGui.QColor(255, 50, 50)))
                self.w_publish_file.tableWidget_shots.setItem(i, 4, edl_duration_item)
                
                if edl_cut_in < 1000:
                    cut_in_item.setBackground( QtGui.QBrush(QtGui.QColor(180, 120, 30)))
                
                newItem = QtGui.QTableWidgetItem( d_edt_shots[shot_name]['mov'] )
                self.w_publish_file.tableWidget_shots.setItem(i, 5, newItem)
        return


    def on_pick_edl(self):
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

        browse_root = self._prepare_final_cut_browse()

        pick_dialog.setDirectory(browse_root)
        pick_dialog.setNameFilters(["EDL (*.edl)"])
        pick_dialog.exec_()
        l_files = pick_dialog.selectedFiles()
        if len(l_files) == 0:
            return

        self._unlock_selected_final_cut_dirs(l_files)

        edl_file = l_files[0]
    
        if os.path.isfile( edl_file):
            self.w_publish_file.lineEdit_edl.setText(edl_file)

        try:
            self.on_load()
        except:
            self.print_log(traceback.format_exc(), QtGui.QColor(255, 50, 50))

        return

    def pick_preview(self):
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            PublishDialog.pick_preview(self)
            return

        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

        browse_root = self._prepare_final_cut_browse()
        pick_dialog.setDirectory(browse_root)
        pick_dialog.setNameFilters(
            ["Images/Video(*.jpg  *.jpeg *.tiff *.tiff *.exr *.png *.mov)", "All Files(*.*)"])
        pick_dialog.exec_()
        l_files = pick_dialog.selectedFiles()

        self._unlock_selected_final_cut_dirs(l_files)

        for file_path in l_files:
            file_path_str = str(file_path)
            if file_path_str.lower().endswith('.mov'):
                self.w_file.listWidget_preview.clear()
            else:
                i = self.w_file.listWidget_preview.count()
                if i == 1 and str(self.w_file.listWidget_preview.item(0).text()).lower().endswith('.mov'):
                    self.w_file.listWidget_preview.clear()

            self.w_file.listWidget_preview.addItem(file_path_str.replace('\\', '/'))

        if self.w_file.listWidget_preview.count() > 0 and self.page_permit < 2:
            self.page_permit = 2

