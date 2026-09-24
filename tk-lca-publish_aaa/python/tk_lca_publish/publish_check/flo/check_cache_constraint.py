# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import os
import sys
import pymel.core as pm

import lay.utilities.anim_curve_ops as aco;reload(aco)

CONSTRAINT_TYPES = ['parentConstraint', 'pointConstraint','aimConstraint','orientConstraint','scaleConstraint']
ANIMCURVE_TYPES = ['animCurve', 'animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU', 
                   'animCurveUA', 'animCurveUL', 'animCurveUT', 'animCurveUU']

# All system check classes will use StdCheck as the class name.
class StdCheck():
    """
    """
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"gpuCache上没有动画的情况下不能有约束"
        self.description = u"gpuCache上没有动画的情况下不能有约束, 位移可以通过直接移动AR节点来实现"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            gpuCaches = pm.ls(type = 'gpuCache')
            self.gpuConns = {}
            for gpu in gpuCaches:
                gpu_full_path = gpu.fullPath()
                if '|assets|lay' in gpu_full_path:
                    continue
                gpu_parent = pm.listRelatives(gpu, parent = True)[0]
                self.gpuConns = self.get_constraint_dest_list(str(gpu_parent), self.gpuConns)
                self.gpuConns = self.get_constraint_dest_list(str(gpu), self.gpuConns)
            
            if self.gpuConns:
                self.can_be_auto_fixed, self.can_not_be_fixed = self.get_auto_fixed_list(self.gpuConns)
                msg = u''
                if self.can_be_auto_fixed:
                    msg += u'以下gpuCache节点上没有动画但是有约束, 可自动修复：\n'
                    for key in self.can_be_auto_fixed:
                        msg += key + ': ' + str(self.can_be_auto_fixed[key]) + '\n'
                if self.can_not_be_fixed:
                    msg += u'\n以下gpuCache节点上有动画，不可自动修复，请Artist根据实际情况修改：\n'
                    for key in self.can_not_be_fixed:
                        msg += key + ': ' + str(self.can_not_be_fixed[key]) + '\n'
                    return msg
            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            self.auto_fix_it(self.can_be_auto_fixed)
            return ''
        except:
            return traceback.format_exc()

    def get_constraint_dest_list(self, node_name, gpuConns = {}):
        """
        """
        conns_list = []
        conns = list(set(pm.listConnections(node_name, destination = True, type = CONSTRAINT_TYPES)))
        if conns:
            for conn in conns:
                #conn_list = list(set(pm.listConnections(conn, source = True)))
                conn_list = conn.getTargetList()
                if conn_list:
                    conns_list.extend(conn_list)
                if conns_list:
                    gpuConns[str(node_name)] = conns_list
        return gpuConns
    
    def check_conn_deletable(self, gpuConn, frame_range):
        """
        if the gpuConn can be deleted, return True, else, return False
        """
        could_be_del = True
        animCurves = list(set(pm.listConnections(gpuConn, type = ANIMCURVE_TYPES)))
        if animCurves:
            for animCurve in animCurves:
                is_static = aco.is_static(animCurve, (frame_range[0], frame_range[1]))
                if not is_static:
                    could_be_del = False
                    break
        
        return could_be_del
    
    def get_auto_fixed_list(self, gpuConns):
        """
        """
        minTime = pm.playbackOptions(minTime = True, query = True)
        maxTime = pm.playbackOptions(maxTime = True, query = True) 
        can_not_be_fixed = {}
        can_be_auto_fixed = {}
        for gpu_key in gpuConns:
            could_be_del = True
            for gpuConn in gpuConns[gpu_key]:
                could_be_del = self.check_conn_deletable(gpuConn, (minTime, maxTime))
                if not could_be_del:
                    break
            
            if could_be_del:
                can_be_auto_fixed[gpu_key] = gpuConns[gpu_key]
            else:
                can_not_be_fixed[gpu_key] = gpuConns[gpu_key]
        return can_be_auto_fixed, can_not_be_fixed
    
    def auto_fix_it(self, auto_fixed_dict):
        """
        auto_fixed_dict: dict, key is the node, value is its constraint sources, 
        e.g. {'m30_city:club_inside_asb:alcohol_d39_AR': [nt.Transform(u'club_inside_asb_alcohol_d39_AR_con')]
        """
        for key in auto_fixed_dict:
            gpu_w = pm.xform(str(key), query = True, matrix = True, worldSpace = True)
            pm.delete(auto_fixed_dict[key])
            pm.xform(str(key), matrix = gpu_w, worldSpace = True)
        

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



