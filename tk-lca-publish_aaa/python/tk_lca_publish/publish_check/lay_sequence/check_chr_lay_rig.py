# -*- coding:utf-8 -*-


import os
import maya.cmds as cmds
import pymel.core as pm
import lay.lca_asset_switch.switch_rig_new as srn

reload(srn)


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查chr的绑定类型是是否 lay rig"
        self.description = u"传递下游chr,切lay rig"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        self.no_lay_rig = []
        return

    def run_check(self):
        self.no_lay_rig = []
        all_refs = pm.ls(type = 'reference')
        for ref_node in all_refs:
            if ref_node.name() == 'sharedReferenceNode' or '_sharedReferenceNode' in ref_node.name():
                continue
            if ref_node.name() == '_UNKNOWN_REF_NODE_':
                pm.delete(ref_node)
                continue
            if ref_node.isLoaded():
                filename = ref_node.fileName(True, True, False).replace('.ma', '').replace('.mb', '')
                if filename == 'camera':
                    continue
                path = ref_node.referenceFile().path
                if '/chr/' in path and (not os.path.dirname(ref_node.referenceFile().path).endswith('.rig.rigging_layout')):
                    ns = ref_node.associatedNamespace(True)
                    self.no_lay_rig.append(ns + ':master')
        if self.no_lay_rig:
            return u'绑定类型不是lay rig: %s' % self.no_lay_rig
        else:
            return ''

    def run_fix(self):
        '''Auto Fix'''
        if self.no_lay_rig:
            cmds.select(self.no_lay_rig)
            srn.main("layout", show_ui=True)

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

