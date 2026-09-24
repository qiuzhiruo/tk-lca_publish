# coding=utf8
# Time    : 6/7/22 3:55 PM
# Author  : MengWei
# File    : check_vfx_grp.py

import os
import re
import sys

import traceback,platform
import pymel.core as pm
import maya.cmds as cmds

LAY_VFX = '|assets|lay|VFX'
REF_VFX = '|assets|lay|VFX:assets'
REF_VFX_OUTASSETSGRP = 'VFX:assets'
LAY_GRP = '|assets|lay'
REF_VFX_NODE = 'VFXRN'

system = platform.platform()
############################################

if 'Window' in system:
    scene_name = cmds.file(q=1, location=1)
    scene_proj = scene_name.split('/')[2]
    scene_seq = scene_name.split('/')[4]
    scene_shot = scene_name.split('/')[5]
    if scene_proj == 'rws':
        WORK_VFX_PATH = 'W:/projects/%s/shot/%s/%s/ani/task/maya/vfx_ref'
    else:
        WORK_VFX_PATH = 'W:/projects/%s/shot/%s/%s/ani/task/maya/extra_data/VFX'


else:
    scene_name = cmds.file(q=1, location=1)
    scene_proj = scene_name.split('/')[4]
    scene_seq = scene_name.split('/')[6]
    scene_shot = scene_name.split('/')[7]
    if scene_proj == 'rws':
        WORK_VFX_PATH = '/mnt/work/projects/%s/shot/%s/%s/ani/task/maya/vfx_ref'
    else:
        WORK_VFX_PATH = '/mnt/work/projects/%s/shot/%s/%s/ani/task/maya/extra_data/VFX'


############################################


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否有VFX组"
        self.description = u"检查是否有VFX组|assets|lay|VFX"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        if not pm.objExists(LAY_VFX):
            return u'{}组不存在（需要有这个组）。'.format(LAY_VFX)
        return ''

    def run_fix(self):
        '''Auto Fix'''
        
        

        scene_name = pm.sceneName()
        if 'Window' in system:
            scene_name = pm.sceneName()
            scene_proj = scene_name.split('/')[2]
            scene_seq = scene_name.split('/')[4]
            scene_shot = scene_name.split('/')[5]
            
        else:
            scene_name = pm.sceneName()
            scene_proj = scene_name.split('/')[4]
            scene_seq = scene_name.split('/')[6]
            scene_shot = scene_name.split('/')[7]
            
        
        work_vfx_path = WORK_VFX_PATH % (scene_proj, scene_seq, scene_shot)


        if cmds.objExists(REF_VFX):
            result = cmds.confirmDialog(bgc = [0.628, 0.628, 1],title=u'提示 !!!',message=(u'文件中 存在 " %s " \n点击 OK 将 import 进来！' % REF_VFX),button=('OK', 'Cancel'),defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')
            if result != 'OK':
                return
            self._import_vfx(work_vfx_path)
            
        else:
            if os.path.exists(work_vfx_path):
                all_vfx_version = sorted(os.listdir(work_vfx_path))
                if all_vfx_version == []:
                    result = cmds.confirmDialog(bgc = [0.628, 0.628, 1],title=u'提示 !!!',message=(u'文件中 不存在 " %s " \n且 未检测到 有备份的 VFX \n点击 OK 将创建一个 空 的 VFX 组！' % LAY_VFX),button=('OK', 'Cancel'),defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')
                    if result != 'OK':
                        return
                    new_vfx_grp = cmds.group( em=True, name=('VFX'))
                    cmds.parent(new_vfx_grp, LAY_GRP)
                else:
                    result = cmds.confirmDialog(bgc = [0.628, 0.628, 1],title=u'提示 !!!',message=(u'文件中 不存在 " %s " \n且 检测到 有备份的 VFX \n点击 OK 将 import 最新版本的 VFX ！' % LAY_VFX),button=('OK', 'Cancel'),defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')
                    if result != 'OK':
                        return
                    self._import_vfx(work_vfx_path)
            else:
                result = cmds.confirmDialog(bgc = [0.628, 0.628, 1],title=u'提示 !!!',message=(u'文件中 不存在 " %s " \n且 未检测到 有备份的 VFX \n点击 OK 将创建一个 空 的 VFX 组！' % LAY_VFX),button=('OK', 'Cancel'),defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')
                if result != 'OK':
                    return
                new_vfx_grp = cmds.group( em=True, name=('VFX'))
                cmds.parent(new_vfx_grp, LAY_GRP)
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
    def _clean_ref_vfx(self):
        if cmds.objExists(REF_VFX):
            if cmds.referenceQuery(REF_VFX, inr=1):
                cmds.file(rfn=REF_VFX_NODE, rr=1)
            else:
                self._unlock_nodes(REF_VFX)
                cmds.delete(REF_VFX)
                cmds.namespace(rm='VFX', mnp=1)
    def _clean_unload_vfx(self):
        all_referenceNodes = cmds.ls(rf=1)
        for ref_node in all_referenceNodes:
            ref_load_yes_no = cmds.referenceQuery(ref_node,il=1)
            if not ref_load_yes_no:
                if 'VFXRN' in ref_node:
                    cmds.file(rfn=ref_node, rr=1)
                if cmds.namespace(exists='VFX'):
                    cmds.namespace(rm='VFX', mnp=1)
    def _import_vfx(self,work_vfx_path):

        # clean ref vfx
        self._clean_ref_vfx()
        # clean unload ref vfx
        self._clean_unload_vfx()
        print u'------------- 清除 VFX 成功 -------------'
        all_vfx_version = sorted(os.listdir(work_vfx_path))
        ref_vfx_version = all_vfx_version[-1]
        ref_vfx_path = work_vfx_path + '/' + ref_vfx_version
        if os.path.exists(ref_vfx_path):
            if cmds.namespace(exists='VFX'):
                cmds.namespace(rm='VFX', mnp=1)
            cmds.file(ref_vfx_path, i=1, type='mayaAscii', namespace='VFX')

            if cmds.objExists(LAY_VFX):
                self._unlock_nodes(LAY_VFX)
                cmds.delete(LAY_VFX)
            pm.select(REF_VFX_OUTASSETSGRP)
            tops = pm.ls(sl=True)
            for top in tops:
                all = pm.listRelatives(top, allDescendents=True)
                all.append(top)
                for c in all:
                    pm.lockNode(c, lock=False)
            cmds.parent(REF_VFX_OUTASSETSGRP, LAY_GRP)

            if len(cmds.ls('|assets|lay|assets', dag=1, long=1)) == 1:
                cmds.delete('|assets|lay|assets')
            cmds.parent('|assets|lay|VFX:assets|VFX:lay|VFX:VFX', LAY_GRP)
            if cmds.namespace(exists='VFX'):
                cmds.namespace(rm='VFX', mnp=1)

            # cmds.parent('|assets|lay|assets|lay|VFX',LAY_GRP)

            if len(cmds.ls('|assets|lay|assets|lay', dag=1, long=1)) == 1:
                cmds.delete('|assets|lay|assets|lay')
            if len(cmds.ls('|assets|lay|assets', dag=1, long=1)) == 1:
                cmds.delete('|assets|lay|assets')

            ref_VFXLay_attr_tx = cmds.setAttr(LAY_VFX + '.translateX', 0)
            ref_VFXLay_attr_ty = cmds.setAttr(LAY_VFX + '.translateY', 0)
            ref_VFXLay_attr_tz = cmds.setAttr(LAY_VFX + '.translateZ', 0)
            ref_VFXLay_attr_rx = cmds.setAttr(LAY_VFX + '.rotateX', 0)
            ref_VFXLay_attr_ry = cmds.setAttr(LAY_VFX + '.rotateY', 0)
            ref_VFXLay_attr_rz = cmds.setAttr(LAY_VFX + '.rotateZ', 0)

            cmds.confirmDialog(bgc=[0.667, 1, 0.667], title=u"Reference VFX 成功 ！！！",
                                message=u"Reference VFX 成功 ！！！\nVFX 版本为 ：%s\n有疑问的话，请联系 TD ！！！" % ref_vfx_version)
        else:
            cmds.confirmDialog(bgc=[1, 0.6, 0.6], title=u"失败 ！！！",
                               message=u"失败，当前镜头文件并未备份过 VFX ！！！\n并且，文件中也没有发现 VFX 组 ！！！\n有疑问的话，请联系 TD ！！！")
