# -*- coding:utf-8 -*-

####################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Zhang Shirui
#
# Date: 2015.07
#
# Description: 
#
# Assure objects in each "combine_*" set are of the same topology.
#
###################################################################

import os
import traceback
import hashlib
from xml.dom.minidom import Document
import pymel.core as pm
import maya.api.OpenMaya as om
from proc.function_running_time import record_time

def get_topo(object):
    shape_node = object.getShape()
    sl = om.MSelectionList()
    sl.add(shape_node.fullPath())
    mesh_dag = sl.getDagPath(0)
    mesh_mfn = om.MFnMesh(mesh_dag)
    v = mesh_mfn.getVertices()
    v_str0 = '[' + ', '.join([str(j) for j in v[0]]) + ']'
    v_str1 = '[' + ', '.join([str(j) for j in v[1]]) + ']'
    topology = hashlib.md5( v_str0 + ' ' + v_str1).hexdigest()
    return topology

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查combine集合下物体的拓扑结构。"
        self.description = u"每个combine_*集合下物体的拓扑结构须保持一致。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            all_sets = pm.ls(type='objectSet')

            for i in all_sets:
                if not i.name().startswith('combine_'):
                    continue
                
                set_objs = i.members()
                topo_dict = {}
                result_dict = {}
                
                if len(set_objs) == 0:
                    return u'集合' + i.name() + u'为空，请清除该集合。'
                
                elif len(set_objs) == 1:
                    return u'集合' + i.name() + u'仅包含1个成员，请添加其他需要合并的物体或者清除该集合。'
                
                else:
                    for o in set_objs:
                        topology = get_topo(o)
                        if not topo_dict.has_key(topology):
                            temp = pm.duplicate(o, rr=True)[0]
                            temp.scaleBy((-1,1,1))
                            pm.makeIdentity(temp, apply=True, t=True, r=True, s=True, n=False, pn=True)
                            topology_m = get_topo(temp)
                            pm.delete(temp)
                            l = [o]
                            topo_dict[topology] = l
                            topo_dict[topology_m] = l
                        else:
                            topo_dict[topology].append(o)
                    
                    for j in topo_dict.values():
                        result_dict[hex(id(j))] = j
                    if not len(result_dict) == 1:            
                        return_string = u'集合' + i.name() + u'中存在不同的拓扑结构。分类如下：\n'
                        for t in result_dict.values():
                            return_string = return_string + t[0].name() + u'等' + str(len(t)) + u'个物体\n'
                        return return_string

            return ''

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


