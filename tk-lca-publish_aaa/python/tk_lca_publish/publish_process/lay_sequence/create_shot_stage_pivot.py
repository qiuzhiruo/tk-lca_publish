# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import os
import traceback
import copy
import math
import pymel.core as pm
import pymel.core.nodetypes as nt

import publish_process.lay.create_stage_pivot as csp;reload(csp)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录每个镜头的场景表演区中心到shotgun"
        self.description = u"记录每个镜头的场景表演区中心到shotgun"
        
        return

    def setup_init(self):
        """
        """
        self.proj = self.dialog.sg.find_one('Project', [['id', 'is', self.dialog.project['id']]], ['sg_unit_length'])
        if self.proj['sg_unit_length'] is not None:
            self.unit = self.proj['sg_unit_length']
        else:
            self.unit = 'dm'
        self.pivot_step = int(csp.D_UNITS[self.unit] / csp.PIVOT_DIVISION_FACTOR)
        
        csp_instance = csp.StdProcess(self.dialog)
        csp_instance.proj = self.proj
        csp_instance.unit = self.unit
        csp_instance.pivot_step = self.pivot_step
        
        return csp_instance

    def create_shot_pivot(self, shot_name, pivot_grp_node, csp_instance):
        """
        """
        obj_set = shot_name + '_assets'
        shot_cam = shot_name + '_cam'
        if pm.objExists(obj_set):
            shot_objs = nt.ObjectSet(obj_set).members()
        else:
            shot_objs = pm.listRelatives('|assets|chr', children = True)
        print 'obj_set', obj_set
        print 'shot_cam', shot_cam
        print 'shot_objs', shot_objs
        
        shot_node = shot_name + '_shot'
        if pm.objExists(shot_node):
            csp_instance.cut_in = int(pm.getAttr(str(shot_node) + '.startFrame'))
            csp_instance.cut_out = int(pm.getAttr(str(shot_node) + '.endFrame'))
        else:
            csp_instance.cut_in = int(pm.playbackOptions(query = True, minTime = True))
            csp_instance.cut_out = int(pm.playbackOptions(query = True, maxTime = True))
        print 'cut in', csp_instance.cut_in
        print 'cut out', csp_instance.cut_out
        pm.currentTime(csp_instance.cut_in )
        
        if not pm.objExists(pm.PyNode(shot_cam)):
            return 'Failed to find camera: ' +  shot_cam
        
        csp_instance.cam = pm.PyNode(shot_cam)
        
        shot_pivot = shot_name + '_locator'
        shot_pivot_full = pivot_grp_node.fullPath() + '|' + shot_pivot
        if pm.objExists(shot_pivot_full):
            pm.delete(shot_pivot_full)
        
        loc = csp_instance.create_pivot(locname = shot_pivot, parent = None)
        print 'create_shot_stage_pivot::stage pivot value: ', loc
        
        return ''

    def proceed(self):
        try:
            csp_instance = self.setup_init()
            
            pivot_root = '|assets|lay'
            pivot_grp = 'pivot_grp'
            full_pivot_grp = pivot_root + '|' + pivot_grp                   # |assets|lay|pivot_grp
            if not pm.objExists(full_pivot_grp):
                pivot_grp_node = pm.createNode('transform', name = pivot_grp, parent = pivot_root)
            else:
                pivot_grp_node = pm.PyNode(full_pivot_grp)
            
            for data in self.dialog.shots_preview_data:
                shot_name = data['shot_info']['code']
                print 'shot_name:', shot_name
                result = self.create_shot_pivot(shot_name, pivot_grp_node, csp_instance)
                if result:
                    return result
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

