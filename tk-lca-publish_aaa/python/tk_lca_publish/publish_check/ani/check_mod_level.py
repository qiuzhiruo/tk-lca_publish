# -*- coding:utf-8 -*-

import traceback
import os
import maya.cmds as cmds
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查reference资产的各种高低模切换属性"
        self.description = u"reference资产的高低模切换属性需要切换到高模选项"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        self.lod_attrs = {
            'visibility_ctrl': {'model_level': 0, 'mod_low_high_switch': 1},
        }
        return

    def run_check(self):
        try:
            self.invalid_nodes = {}

            for k, v in self.lod_attrs.iteritems():
                ctrls = pm.general.ls(k, recursive=True, referencedNodes=True)
                ctrls = list(set(ctrls))
                for c in ctrls:
                    for a in v:
                        attr_full = '{}.{}'.format(c.name(), a)
                        if pm.hasAttr(c, a) and not pm.getAttr(attr_full, lock=True) and pm.getAttr(attr_full) != v[a]:
                            self.invalid_nodes[attr_full] = v[a]

            if self.invalid_nodes:
                return u'以下资产切换高低模的属性设置值不对:\n' + '\n'.join([u'{} 应设置为 {}'.format(k, v) for k, v in self.invalid_nodes.iteritems()])

            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        """Auto Fix"""
        try:
            for k, v in self.invalid_nodes.iteritems():
                if cmds.objExists(k):
                    if cmds.listConnections(k, s=True, d=False, type='animCurve'):
                        for f in cmds.keyframe(k, q=True, timeChange=True):
                            cmds.setKeyframe(k, time=(f, f), value=v)
                    else:
                        cmds.setAttr(k, v)
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

