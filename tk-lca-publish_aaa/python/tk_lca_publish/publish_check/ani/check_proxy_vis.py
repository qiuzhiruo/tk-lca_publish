# -*- coding:utf-8 -*-

import traceback
import os
import pymel.core as pm
import production.mayautils as mutils
import ani.lca_asset_switch.functions as functions
# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查reference资产的Proxy Vis"
        self.description = u"reference资产的Proxy资产的Vis需要打开"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            self.invalid_nodes = []
            ctrls = pm.general.ls('visibility_ctrl', recursive=True, referencedNodes=True)
            ctrls = list(set(ctrls))
            for r in ctrls:
                pm.select(r)
                reference = functions.getReferencesFromSelection(include_assembly = True)
                ignore = False
                if reference:
                    for ref in reference:
                        path = functions.getReferencePath(ref)
                        if path and ('/prp/' in path or 'prince_white_dragon' in path):
                            ignore = True
                if ignore:
                    continue 

                attrname = r.name()+'.proxy_vis'
                if pm.hasAttr(r,'proxy_vis') and not pm.getAttr(attrname,lock=True):
                    if pm.getAttr(attrname) == 0: self.invalid_nodes.append(attrname)

            if self.invalid_nodes:
                return u'发现proxy_vis为0节点：' + ', '.join(self.invalid_nodes)

            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            for i in self.invalid_nodes:
                if pm.objExists(i):
                    pm.setAttr(i, 1)
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

