# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: huangxin
#
# Date: 2018.5.29
#
# Description: As the description shows below
#
############################################

import traceback,os
import plt.xg_tessa.xgenio as pxio
from sgtk.platform.qt import QtCore, QtGui

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否启用LOD"
        self.description = u"loIndex属性没有设置LOD，或者打成高模，需要重新检查确认"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def check_lod(self):
        no_lod_list = []
        try:
            import maya.cmds as cmds
            import xgenm.xgGlobal as xgg
            des_list = [des[:-5] for des in cmds.ls(type="xgmDescription")]
            de = xgg.DescriptionEditor
            for des in des_list:
                de.setCurrentDescription(str(des))
                pal = de.currentPalette()
                expression = de.getAttr("ArchivePrimitive","loIndex")
                if '$aLOD' not in expression and int(expression.split('+')[-2]) == 0:
                    no_lod_list.append(pal+'/'+des)
        except:
            output_cache = str(self.dialog.w_publish_file.lineEdit_cache.text())
            all_files = StdCheck.get_xgen_file(output_cache)
            for xg_f in all_files:
                no_lod_list = StdCheck.check_xgfile_lod(xg_f, no_lod_list)

        return no_lod_list

    @staticmethod
    def check_xgfile_lod(xg_f, no_lod_list):
        xg_data = pxio.XgenReader(xg_f).init_xgdata()
        desc_list= xg_data.get_desc_name_list()
        no_lod_list=[]
        pal = os.path.basename(xg_f).split('.')[0]
        for des in desc_list:
            xg_content = xg_data.get_desc_attr_str(des, 'ArchivePrimitive', 'files')[0]
            loIndex = xg_data.get_desc_attr_str(des, 'ArchivePrimitive', 'loIndex')[0]
            if '$aLOD' not in loIndex and int(loIndex.split('+')[-2]) == 0:
                no_lod_list.append(pal+'/'+des)

        return no_lod_list

    @staticmethod
    def get_xgen_file(output_folder):
        import glob
        xg_f=[]
        xg_f.extend(glob.glob(output_folder+'/cache/*/xgen/collections/*/*.xgen'))
        return xg_f

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
                'subject':"[警告] PLT 没有设置lod",
                'user':user}
                
        noteid=sg.create('Note',noteDict)

    def run_check(self):
        try:
            no_lod_list = self.check_lod()

            if no_lod_list:
                info = u'没有设置lod并使用高模: \n'+'\n'.join(no_lod_list)
                
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


