# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import sys
import os
import copy

import tank
import pymel.core as pm
import pymel.core.nodetypes as nt
import maya.OpenMaya as om

import lay.lca_map_ar.utils.mayaOperations as mayaOps;reload(mayaOps)
import lay.lca_root_con.record_rough_shot_ar_status_for_ani as rrsasfa;reload(rrsasfa)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录各个镜头的ar状态"
        self.description = u"在split_into_shots之前记录,各个镜头的ar状态到lay publish文件夹, ar_status.txt中, "
        return

    def get_all_ar_status(self):
        """
        """
        ar_dict = {}
        l_ar = pm.ls(type = 'assemblyReference', l =1)
        for l in l_ar:
            current = l.getActiveLabel()
            if current == '':
                current = 'None'
            ar_dict[l.name()] = current
        return ar_dict
    
    def shot_ar_visibility_status(self, ar_dict):
        """
        """
        shot_ar_dict = copy.deepcopy(ar_dict)
        ars = pm.ls(type = 'assemblyReference', l =1)
        for ar in ars:
            arObj = om.MObject()
            arDagPath = om.MDagPath()
            arObj = mayaOps.nodeFromName(str(ar))
            arDagPath = mayaOps.get_node_dagPath(arObj)
            
            fullPath = arDagPath.fullPathName()
            if not fullPath.startswith('|assets|lay'):
                parents = fullPath.split('|')[3:]
                for parent in parents:
                    if not pm.getAttr(parent + '.visibility'):
                        if ar.name() in shot_ar_dict:
                            shot_ar_dict[ar.name()] = 'Invisible'
                        break
        return shot_ar_dict
    
    def proceed(self):
        try:
            ar_dict = self.get_all_ar_status()
            for data in self.dialog.shots_preview_data:
                shot_name = data['shot_info']['code']
                shot = shot_name + '_shot'
                pm.currentTime(pm.getAttr(str(shot) + '.startFrame'))
                shot_ar_dict = self.shot_ar_visibility_status(ar_dict)
                
                ar_info_file = os.path.join(data['version_dir'], 'ar_status.txt')
                with open(ar_info_file,'w') as op:
                    for ar_name in sorted(shot_ar_dict.keys()):
                        op.write(ar_name + '\t' + shot_ar_dict[ar_name] + '\n')
            # 增加 额外输出 ar 的 标签状态,显示隐藏信息 记录到 txt 内,放到 单个镜头的 work 盘下
            rrsasfa.main()
            
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description



