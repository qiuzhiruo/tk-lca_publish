# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: Check to see if a face has too many (more than 4) edges.
#
########################################################################################

import traceback
import maya.cmds as cmds
import maya.api.OpenMaya as om
import pymel.core as pm
from proc.function_running_time import record_time

TR_ATTRS = ['inheritsTransform', 'translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX',
            'scaleY', 'scaleZ', 'visibility', 'shear', 'rotateAxis', 'translate', 'rotate', 'scale', 'shearXY',
            'shearXZ', 'shearYZ', 'rotateAxisX', 'rotateAxisY', 'rotateAxisZ']


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查并解锁模型属性。"
        self.description = u"检查模型属性是否被锁定，如果锁定自动解锁。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            if not cmds.objExists('|master|poly|hi'):
                return u'没有找到 |master|poly|hi 组。'

            lock_meshs = []
            l_meshes = pm.listRelatives('|master', ad=True, type='transform', path=True)
            if not l_meshes:
                return ""
            l_meshes.append(pm.PyNode('master'))

            for mesh in l_meshes:
                pm.lockNode(mesh, lock=0)
                for attr_name in TR_ATTRS:
                    attr = mesh.attr(attr_name)
                    if attr.isLocked():
                        pm.setAttr(attr, l=False)

                    if attr.isLocked():
                        lock_meshs.append(mesh)

            if len(lock_meshs) > 0:
                return u'这些模型有属性被锁定： ' + ' '.join(list(set(lock_meshs)))

            # disable set poly.inheritsTransform
            # cmds.setAttr('poly.inheritsTransform',l=False)
            # cmds.setAttr('poly.inheritsTransform',0)


            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            l_meshes = cmds.listRelatives('|master|poly|hi', ad=True, type='transform', path=True)
            for mesh in l_meshes:
                pm.lockNode(mesh, lock=0)
                for attr in TR_ATTRS:
                    pm.setAttr(mesh + '.' + attr, l=False)

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
