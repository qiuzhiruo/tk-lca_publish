# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: XiangQuan
#
# Date: 2015.08
#
# Description:
#
############################################

import os
import sys
import traceback
import shutil
from xml.dom.minidom import Document, parse

import pymel.core as pm
import maya.OpenMaya as OpenMaya
import maya.app.general.editUtils as editUtils
from maya.maya_to_py_itr import PyEditItr

import production.CacheUtils.FilterCacheObjects as cf;

reload(cf)
# import maya.cmds as cmds

# sys.path.append('P:/home/liulu/td_dev_zone/sgtk/tk-lca-publish/python/tk_lca_publish')
from proc import scene_assets;reload(scene_assets)

import lay.utilities.anim_curve_ops as anim_curve_ops;reload(anim_curve_ops)
import publish_process.ani.list_ani_assets as list_ani_assets;reload(list_ani_assets)


# All publish process will use StdProcess as the class name.
class StdProcess():
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.l_assets = []
        
        self.process_name = u"整理reference资产的不必要的约束"
        self.description = u"场景中reference的资产被约束到另一个物体上，但是两者均没有动画时，去掉约束，只保留translate和rotate值。"
        return
    

    def proceed(self):
        """
        just check two levels about an asset's constraints: if a constraint target itself has animation or constraints,
        or it's under more than 1 parent nodes (|assets and |assets|[grp] are out of consideration),
        we take the asset as an node with useful constraint or animation, so we keep its constraints
        and export caches for it
        :return:
        """
        try:
            start_frame = pm.playbackOptions(query = True, minTime = True)
            end_frame = pm.playbackOptions(query = True, maxTime = True)
            laa = list_ani_assets.StdProcess(dialog = None)
            l_ref_assets = scene_assets.getReferenceAssets('|assets')  # e.g. [nt.Transform(u'axuan:master')]

            remove_constraints_dict = {}
            for ref_asset in l_ref_assets:
                is_constrainted = laa.check_ref_constrain(ref_asset)  # 'constrained', 'constrained_trans' or ''
                if is_constrainted:
                    keep_it = False
                    constraints = [constraint for constraint in
                                   pm.listRelatives(ref_asset, ad = True, type = 'constraint') if
                                   not constraint.isReferenced()]
                    if len(constraints) > 1:
                        keep_it = True
                        break
        
                    targets = constraints[0].getTargetList()
                    for target in targets:
                        target_constrainted = laa.check_ref_constrain(target)
                        if target_constrainted:
                            keep_it = True
                            break
                        if anim_curve_ops.is_vaildly_animated(target, (start_frame, end_frame)):
                            keep_it = True
                            break
                        parent_num = len(target.fullPath().split('|'))
                        # e.g. parent_split = [u'',u'assets',u'lay',u'b70_a_main_con',u'ship_global_ctrl_con_sec_ctrl', ...]
                        if parent_num > 5:
                            keep_it = True
                            break
        
                    if not keep_it:
                        if ref_asset in remove_constraints_dict:
                            remove_constraints_dict[ref_asset].extend(constraints)
                        else:
                            remove_constraints_dict[ref_asset] = constraints
        
            if remove_constraints_dict:  # e.g. [nt.Transform(u'axuan:master')]
                for asset in remove_constraints_dict:
                    print 'delete constraints: ', asset
                    constraints = remove_constraints_dict[asset]
                    pm.delete(constraints)
        
            return ""
        except:
            return traceback.format_exc()
    
    
    def get_process_name(self):
        return self.process_name
    
    def get_description(self):
        return self.description

