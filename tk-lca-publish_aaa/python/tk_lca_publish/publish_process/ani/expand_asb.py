# -*- coding:utf-8 -*-

import os
import traceback

import maya.cmds as cmds
import pymel.core as pm


def expand_asb_ar(asb_node):
    if not cmds.objExists(asb_node):
        return
    file_name = os.path.basename(cmds.getAttr('{}.definition'.format(asb_node)))
    if file_name.endswith('_asb.ma') or file_name.endswith('_asb.mb'):
        if pm.assembly(asb_node,q=1,activeLabel=1)!='':
            if not cmds.assembly(asb_node, q=True, al=True).endswith('_asb.ma'):
                asb_name = cmds.getAttr('{}.definition'.format(asb_node)).split('/')[-1].split('.')[0]
                cmds.assembly(asb_node, e=True, active='{}.ma'.format(asb_name))
            for i in cmds.listRelatives(asb_node, ad=True, type='assemblyReference'):
                expand_asb_ar(i)
    elif file_name.endswith('_scn.ma') or file_name.endswith('_scn.mb'):
        if not cmds.assembly(asb_node, q=True, al=True).endswith('_scn.ma'):
            scn_name = file_name.split('.')[0]
            cmds.assembly(asb_node, e=True, active='{}.ma'.format(scn_name))
        for i in cmds.listRelatives(asb_node, ad=True, type='assemblyReference'):
            expand_asb_ar(i)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"展开asb或scn的所有层级"
        self.description = u"展开asb或scn所有层级, 不然输出的xml数据会不全, 导致下游出错"
        return

    def proceed(self):
        try:
            expand_grp = ['|assets|asb', '|assets|scn']
            for eg in expand_grp:
                if not cmds.objExists(eg):
                    continue
                eg_ar = cmds.listRelatives(eg, c=True)
                if not eg_ar:
                    continue
                for single_ar in eg_ar:
                    if not cmds.objectType(single_ar) == 'assemblyReference':
                        continue
                    expand_asb_ar(single_ar)
            # expend_asb_ar("yangjian_big_boat_asb_AR")
            # expend yangjian bianti asb
            # expend_asb_ar("yangjian_big_boat_variation_asb_AR")
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
