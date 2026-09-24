# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Huang Xin
#
# Date: 2018.06.13
#
# 
#
########################################################################################

import os,sys,re,traceback
from sgtk.platform.qt import QtCore, QtGui
import plt.xgen_file_manager.file_utils as pxfu
reload(pxfu)
# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查预渲染耗费内存"
        self.description = u"预渲染内存需要控制在45G以内"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            proj = self.dialog.project['name']
            entity = self.dialog.entity['name']
            if not re.match('[a-z]\d{5}', entity):
                return ''
            mov_file = [str(f_path) for f_path in self.dialog.l_preview_files][0]
            if hasattr(self.dialog.w_publish_file, 'lineEdit_cache'):
                output_cache = str(self.dialog.w_publish_file.lineEdit_cache.text())
                mem_data, setup_time, render_time = pxfu.get_plt_render_info(proj, entity, mov_file, output_cache)
            else:
                mem_data, setup_time, render_time = pxfu.get_plt_render_info(proj, entity, mov_file)
            if mem_data > 45:
                info = u'预渲染内存: %.2fG'%mem_data
                try:
                    result = QtGui.QMessageBox.warning(
                        parent=self.dialog,
                        title=self.check_name,
                        text=info+'\n\n'+u'请确认是否优化！！！',
                        buttons=QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                        defaultButton=QtGui.QMessageBox.Yes
                    )
                except:
                    result = QtGui.QMessageBox.warning(self.dialog, self.check_name, info+'\n\n'+u'请确认是否优化！！！', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                
                if result == QtGui.QMessageBox.Yes:
                    return info
                else:
                    self.send_note(info)

            return ""
        except:
            return entity+' '+mov_file+'\n'+traceback.format_exc()

    def send_note(self, info):
        from production import shotgun_connection
        sg = shotgun_connection.Connection('get_shot_info').get_sg()
        proj = self.dialog.project
        user = self.dialog.user
        leader = {'type': 'HumanUser', 'id': 411, 'name': 'Wang Qi'}
        td = {'type': 'HumanUser', 'id': 495, 'name': 'Huang Xin'}

        noteDict={'project':self.dialog.project,
                'note_links':[self.dialog.entity],
                'content': info.replace('__','\__'),
                'addressings_to':[user, leader, td],
                'sg_note_type':u'通知',
                'subject':"[警告] PLT 预渲染内存超过45G",
                'user':user}
                
        noteid=sg.create('Note',noteDict)
    

    def run_fix(self):
        '''Auto Fix'''
        try:
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



