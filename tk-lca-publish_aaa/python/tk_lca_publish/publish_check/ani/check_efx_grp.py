# -*- coding:utf-8 -*-
# Time    : 01/12/2023 2:55 PM
# File    : check_efx_grp.py

import os
import re
import sys

import traceback,platform
import pymel.core as pm
import maya.cmds as cmds

LAY_TO_EFX = '|assets|lay|TO_EFX'
REF_TO_EFX = '|assets|lay|TO_EFX:assets'
REF_TO_EFX_OUTASSETSGRP = 'TO_EFX:assets'
LAY_GRP = '|assets|lay'
REF_TO_EFX_NODE = 'TO_EFXRN'

system = platform.platform()
############################################

if 'Window' in system:
    scene_name = cmds.file(q=1, location=1)
    scene_proj = scene_name.split('/')[2]
    scene_seq = scene_name.split('/')[4]
    scene_shot = scene_name.split('/')[5]
    if scene_proj == 'rws':
        WORK_TO_EFX_PATH = 'W:/projects/%s/shot/%s/%s/ani/task/maya/efx_ref'
    else:
        WORK_TO_EFX_PATH = 'W:/projects/%s/shot/%s/%s/ani/task/maya/extra_data/TO_EFX'


else:
    scene_name = cmds.file(q=1, location=1)
    scene_proj = scene_name.split('/')[4]
    scene_seq = scene_name.split('/')[6]
    scene_shot = scene_name.split('/')[7]
    if scene_proj == 'rws':
        WORK_TO_EFX_PATH = '/mnt/work/projects/%s/shot/%s/%s/ani/task/maya/efx_ref'
    else:
        WORK_TO_EFX_PATH = '/mnt/work/projects/%s/shot/%s/%s/ani/task/maya/extra_data/TO_EFX'


############################################


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否有TO_EFX组"
        self.description = u"检查是否有TO_EFX组|assets|lay|TO_EFX"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        if not pm.objExists(LAY_TO_EFX):
            return u'{}组不存在（需要有这个组）。'.format(LAY_TO_EFX)
        return ''

    def run_fix(self):
        '''Auto Fix'''
        
        

        scene_name = cmds.file(q=1, sn=1)
        if 'Window' in system:
            scene_name = cmds.file(q=1, sn=1)
            scene_proj = scene_name.split('/')[2]
            scene_seq = scene_name.split('/')[4]
            scene_shot = scene_name.split('/')[5]
            
        else:
            scene_name = cmds.file(q=1, sn=1)
            scene_proj = scene_name.split('/')[4]
            scene_seq = scene_name.split('/')[6]
            scene_shot = scene_name.split('/')[7]
            
        
        work_to_efx_path = WORK_TO_EFX_PATH % (scene_proj, scene_seq, scene_shot)


        if cmds.objExists(REF_TO_EFX):
            result = cmds.confirmDialog(bgc = [0.628, 0.628, 1], title=u'提示 !!!', message=(u'文件中 存在 " %s " \n点击 OK 将 import 进来！' % REF_TO_EFX), button=('OK', 'Cancel'), defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
            if result != 'OK':
                return
            self._import_to_efx(work_to_efx_path)
            
        else:
            if os.path.exists(work_to_efx_path):
                all_to_efx_version = sorted(os.listdir(work_to_efx_path))
                if all_to_efx_version == []:
                    result = cmds.confirmDialog(bgc = [0.628, 0.628, 1], title=u'提示 !!!', message=(u'文件中 不存在 " %s " \n且 未检测到 有备份的 TO_EFX \n点击 OK 将创建一个 空 的 TO_EFX 组！' % LAY_TO_EFX), button=('OK', 'Cancel'), defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
                    if result != 'OK':
                        return
                    new_to_efx_grp = cmds.group(em=True, name=('TO_EFX'))
                    cmds.parent(new_to_efx_grp, LAY_GRP)
                else:
                    result = cmds.confirmDialog(bgc = [0.628, 0.628, 1], title=u'提示 !!!', message=(u'文件中 不存在 " %s " \n且 检测到 有备份的 TO_EFX \n点击 OK 将 import 最新版本的 TO_EFX ！' % LAY_TO_EFX), button=('OK', 'Cancel'), defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
                    if result != 'OK':
                        return
                    self._import_to_efx(work_to_efx_path)
            else:
                result = cmds.confirmDialog(bgc = [0.628, 0.628, 1], title=u'提示 !!!', message=(u'文件中 不存在 " %s " \n且 未检测到 有备份的 TO_EFX \n点击 OK 将创建一个 空 的 TO_EFX 组！' % LAY_TO_EFX), button=('OK', 'Cancel'), defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
                if result != 'OK':
                    return
                new_to_efx_grp = cmds.group(em=True, name=('TO_EFX'))
                cmds.parent(new_to_efx_grp, LAY_GRP)
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

    def _unlock_nodes(self, top):
        all = pm.listRelatives(top, allDescendents=True)
        all.append(top)
        for c in all:
            pm.lockNode(c, lock=False)
    def _clean_ref_efx(self):
        if cmds.objExists(REF_TO_EFX):
            if cmds.referenceQuery(REF_TO_EFX, inr=1):
                cmds.file(rfn=REF_TO_EFX_NODE, rr=1)
            else:
                self._unlock_nodes(REF_TO_EFX)
                cmds.delete(REF_TO_EFX)
                cmds.namespace(rm='TO_EFX', mnp=1)
            self._ref_efx_find()
    def _clean_unload_efx(self):
        all_referenceNodes = cmds.ls(rf=1)
        for ref_node in all_referenceNodes:
            ref_load_yes_no = cmds.referenceQuery(ref_node,il=1)
            if not ref_load_yes_no:
                if 'TO_EFXRN' in ref_node:
                    cmds.file(rfn=ref_node, rr=1)
                if cmds.namespace(exists='TO_EFX'):
                    cmds.namespace(rm='TO_EFX', mnp=1)
    def _import_to_efx(self,work_to_efx_path):

        # clean ref efx
        self._clean_ref_efx()
        # clean unload efx
        self._clean_unload_efx()
            
        print u'------------- 清除 TO_EFX 成功 -------------'


        all_to_efx_version = sorted(os.listdir(work_to_efx_path))
        ref_to_efx_version = all_to_efx_version[-1]
        ref_to_efx_path = work_to_efx_path + '/' + ref_to_efx_version
        if os.path.exists(ref_to_efx_path):
            if cmds.namespace(exists='TO_EFX'):
                cmds.namespace(rm='TO_EFX', mnp=1)
            cmds.file(ref_to_efx_path, i=1, type='mayaAscii', namespace='TO_EFX')

            if cmds.objExists(LAY_TO_EFX):
                self._unlock_nodes(LAY_TO_EFX)
                cmds.delete(LAY_TO_EFX)
            pm.select(REF_TO_EFX_OUTASSETSGRP)
            tops = pm.ls(sl=True)
            for top in tops:
                all = pm.listRelatives(top, allDescendents=True)
                all.append(top)
                for c in all:
                    pm.lockNode(c, lock=False)
            cmds.parent(REF_TO_EFX_OUTASSETSGRP, LAY_GRP)

            if len(cmds.ls('|assets|lay|assets', dag=1, long=1)) == 1:
                cmds.delete('|assets|lay|assets')
            cmds.parent('|assets|lay|TO_EFX:assets|TO_EFX:lay|TO_EFX:TO_EFX', LAY_GRP)
            if cmds.namespace(exists='TO_EFX'):
                cmds.namespace(rm='TO_EFX', mnp=1)

            # cmds.parent('|assets|lay|assets|lay|TO_EFX',LAY_GRP)

            if len(cmds.ls('|assets|lay|assets|lay', dag=1, long=1)) == 1:
                cmds.delete('|assets|lay|assets|lay')
            if len(cmds.ls('|assets|lay|assets', dag=1, long=1)) == 1:
                cmds.delete('|assets|lay|assets')

            ref_VFXLay_attr_tx = cmds.setAttr(LAY_TO_EFX + '.translateX', 0)
            ref_VFXLay_attr_ty = cmds.setAttr(LAY_TO_EFX + '.translateY', 0)
            ref_VFXLay_attr_tz = cmds.setAttr(LAY_TO_EFX + '.translateZ', 0)
            ref_VFXLay_attr_rx = cmds.setAttr(LAY_TO_EFX + '.rotateX', 0)
            ref_VFXLay_attr_ry = cmds.setAttr(LAY_TO_EFX + '.rotateY', 0)
            ref_VFXLay_attr_rz = cmds.setAttr(LAY_TO_EFX + '.rotateZ', 0)

            cmds.confirmDialog(bgc=[0.667, 1, 0.667], title=u"Reference TO_EFX 成功 ！！！",
                               message=u"Reference TO_EFX 成功 ！！！\nTO_EFX 版本为 ：%s\n有疑问的话，请联系 TD ！！！" % ref_to_efx_version)
        else:
            cmds.confirmDialog(bgc=[1, 0.6, 0.6], title=u"失败 ！！！",
                               message=u"失败，当前镜头文件并未备份过 TO_EFX ！！！\n并且，文件中也没有发现 TO_EFX 组 ！！！\n有疑问的话，请联系 TD ！！！")
