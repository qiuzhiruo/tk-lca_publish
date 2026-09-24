# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.06
#
# Description: 
#
########################################################################################

import traceback
import pymel.core as pm
import maya.cmds as cmds

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"Reference 节点不能带命名空间。"
        self.description = u"带 Reference 的资产不能再带命名空间。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            # get mod version
            if cmds.objExists("master.modVersion"):
                mod_version = cmds.getAttr("master.modVersion")

                self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(u"模型版本为：v%s" % mod_version)

            if not pm.objExists('|master'):
                return u'没有找到 |master 组。'

            l_nodes = pm.listRelatives('|master', ad=True, fullPath=True)
            l_ref_nodes = []

            for node in l_nodes:
                if pm.referenceQuery(node, isNodeReferenced=True):
                    l_ref_nodes.append(pm.referenceQuery(node, referenceNode=True))

            l_ref_nodes = list(set(l_ref_nodes))

            d_ref = pm.getReferences()
            l_ref_ns = []
            for ns, file_reference in d_ref.iteritems():
                if ns != ':':
                    if file_reference.refNode in l_ref_nodes:
                        l_ref_ns.append(file_reference.refNode.name())

            if len(l_ref_ns) > 0:
                return  u"有带命名空间的reference: " +  u" ".join(l_ref_ns)

            # asset_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])
            # if asset_info['sg_asset_type'] == 'chr':
            #     if self.dialog.entity['name']=="blanket" or self.dialog.entity['name']=="cape_teen":
            #         notes = cmds.getAttr("rig.notes")
            #         version = notes.split("Version : V")[-1].split(" ")[0]
            #         result = cmp("0.1.5.6", version)
            #         if result:
            #             return  u"%s角色Rig系统是老版本，不可Publish，请用V0.1.5.6版本或更高版本！ " % self.dialog.entity['name']

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



