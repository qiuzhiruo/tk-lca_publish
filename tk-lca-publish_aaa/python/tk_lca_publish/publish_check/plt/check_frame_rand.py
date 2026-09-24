# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: huangxin
#
# Date: 2018.5.8
#
# Description: As the description shows below
#
############################################
import os,sys
import traceback, re
from sgtk.platform.qt import QtCore, QtGui


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查frame随机种类"
        self.description = u"检查tree/shrub随机种类, 超过1发note通知组长和制作人员"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    @staticmethod
    def check_rand_num(output_cache=None):
        error_dict = {}
        try:
            import maya.cmds as cmds
            import xgenm.xgGlobal as xgg

            des_list = [des[:-5] for des in cmds.ls(type="xgmDescription")]
            de = xgg.DescriptionEditor
            
            for des in des_list:
                if 'tree' in des or 'shrub' in des:
                    de.setCurrentDescription(str(des))
                    pal = de.currentPalette()
                    frame_expr = de.getAttr("ArchivePrimitive","frame")
                    over_num = StdCheck.check_frame_expr(frame_expr)
                    if over_num:
                        error_dict[pal+'/'+des] = over_num

        except:
            all_files = StdCheck.get_xgen_file(output_cache)
            for xg_f in all_files:
                des_dict = StdCheck.get_file_expr(xg_f)
                pal = os.path.basename(xg_f).split('.')[0]
                for des, frame_expr in des_dict.items():
                    if 'tree' in des or 'shrub' in des: 
                        over_num = StdCheck.check_frame_expr(frame_expr)
                        if over_num:
                            error_dict[pal+'/'+des] = over_num

        return error_dict

    @staticmethod
    def get_file_expr(xg_f):
        des_dict = {}
        des_start = False
        read_start = False
        card = None
        card_read = False
        pal_read = False
        with open(xg_f) as f:
            for line in f:
                if "Preview" in line and read_start:
                    des_start = False
                    read_start = False
                    card_read = False
                    card = None
                    continue
                elif line.startswith('Palette'):
                    pal_read = True
                    continue
                elif pal_read and 'name' in line:
                    pal_read = False
                    continue
                elif 'Description' in line:
                    des_start = True
                    continue
                elif des_start and line.startswith("\tname"):
                    des_name = line.rstrip('\n').split('\t')[-1]
                    des_dict[des_name]=None
                    read_start = True
                    continue 
                elif read_start and re.findall('\w+\n', line) and "\t" not in line:
                    card = line.rstrip('\n')
                    print "Card",card,read_start
                    card_read = True
                    continue
                elif read_start and card_read and "endAttrs" in line:
                    card_read = False
                    continue
                elif read_start and card and card_read and line.startswith('\t'):
                    attr_name = line.rstrip('\n').split('\t')[1]
                    attr_val = line.rstrip('\n').split('\t')[-1]
                    if attr_name == "frame":
                        des_dict[des_name]=attr_val
        return des_dict

    @staticmethod
    def get_xgen_file(output_folder):
        import glob
        xg_f=[]
        xg_f.extend(glob.glob(output_folder+'/cache/*/xgen/collections/*/*.xgen'))
        return xg_f

    @staticmethod
    def check_frame_expr(expr):
        over_num=[]
        if '(floor(rand' in expr:
            rnd_num=re.findall('floor\(rand\((\d*),(\d*)\)\)', expr)
            over_num = [num for num in rnd_num if int(num[-1]) > 1]
        return over_num

    def send_note(self, info):
        from production import shotgun_connection
        sg = shotgun_connection.Connection('get_shot_info').get_sg()
        proj = self.dialog.project
        user = self.dialog.user
        leader = {'type': 'HumanUser', 'id': 411, 'name': 'Wang Qi'}

        noteDict={'project':self.dialog.project,
                'note_links':[self.dialog.entity],
                'content': info.replace('__','\__'),
                'addressings_to':[user, leader],
                'sg_note_type':u'通知',
                'subject':"[警告] PLT 随机种类超过1",
                'user':user}
                
        noteid=sg.create('Note',noteDict)

    def run_check(self):
        try:
            try:
                output_cache = str(self.dialog.w_publish_file.lineEdit_cache.text())
                error_dict = StdCheck.check_rand_num(output_cache)
            except:
                error_dict = StdCheck.check_rand_num()

            if error_dict:
                info = u'随机种类超过1:\n' 
                for k,v in error_dict.items():
                    info += "%s    %s\n"%(k,v)

                try:
                    result = QtGui.QMessageBox.warning(
                        parent=self.dialog,
                        title=self.check_name,
                        text=info+'\n\n'+u'请确认以上结果是否正确！！！',
                        buttons=QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                        defaultButton=QtGui.QMessageBox.No
                    )
                except:
                    result = QtGui.QMessageBox.warning(self.dialog, self.check_name, info+'\n\n'+u'请确认以上结果是否正确！！！', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                
                if result == QtGui.QMessageBox.Yes:
                    self.send_note(info)
                    return ''
                else:
                    return info
                msgBox.exec_()

            return ''
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty
