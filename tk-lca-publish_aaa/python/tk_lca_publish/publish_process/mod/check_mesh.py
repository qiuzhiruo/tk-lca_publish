# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description: 
#
############################################

import os
import traceback
import hashlib
from xml.dom.minidom import Document
import pymel.core as pm
import maya.api.OpenMaya as om
from proc.mod_diff import Mod_Diff
from proc.function_running_time import record_time



# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"对比精模mesh信息和check的是否一致。"
        self.description = u"对比mesh信息和check的是否一致,避免手动跳过检测。"
        return

    def get_trans(self, root):
        l_nodes = pm.listRelatives(root, type='transform')
        for node in l_nodes:
            if node.type() == 'transform':
                self.l_new_trans.append(node.fullPath())
                self.l_new_trans_name.append(node.fullPath().split('|')[-1])
                self.get_trans(node)
        return



    @record_time(__file__)
    def proceed(self):
        try:
            

            if self.dialog.version_tag == u"粗模":
                return ""

            mesh_xml = os.path.join(os.path.dirname(pm.system.sceneName()),'mesh.xml')
            
            if not os.path.isfile(mesh_xml):
                return ""

            # delete self intersection node

            for self_inter_grp in pm.ls("displayIntersections_self_del_*"):
                pm.delete(self_inter_grp)

            for inter_shape_node in pm.ls(l=True, type="pfxToon"):
                if "_del" in inter_shape_node.name():
                    pm.delete(inter_shape_node.listRelatives(p=1)[0])

            ###############################

            md = Mod_Diff()
            md.parse_xml(mesh_xml)
        
            # write model diff description
            err_missing = u''
            err_new = u''
            err_moved = u''
            err_topology_changed = u''
        
            if len(md.l_missing) != 0:
                err_missing += u'\n有 ' + str(len(md.l_missing)) + u" 个mesh被删除了: "
                if len(md.l_missing) > 5:
                    err_missing += u' '.join(md.l_missing[:5]) + u" ..."
                else:
                    err_missing += u' '.join(md.l_missing)
        
            if len(md.l_new) != 0:
                err_new += u'\n有 ' + str(len(md.l_new)) + u" 个mesh被创建了: "
                if len(md.l_new) > 5:
                    err_new += u' '.join(md.l_new[:5]) + u" ..."
                else:
                    err_new += u' '.join(md.l_new)
        
            if len(md.l_moved) != 0:
                err_moved += u'\n有 ' + str(len(md.l_moved)) + u" 个mesh被改变了层级: "
                if len(md.l_moved) > 5:
                    err_moved += u' '.join(md.l_moved[:5]) + u" ..."
                else:
                    err_moved += u' '.join(md.l_moved)
        
            if len(md.l_topology_changed) != 0:
                err_topology_changed += u'\n 有' + str(len(md.l_topology_changed)) + u" 个mesh被改变了拓扑: "
                if len(md.l_topology_changed) > 5:
                    err_topology_changed += u' '.join(md.l_topology_changed[:5]) + u" ..."
                else:
                    err_topology_changed += u' '.join(md.l_topology_changed)

            err_info = ""

            if len(md.l_missing) > 0:
                err_info+= err_missing
        
            if len(md.l_new) > 0:
                err_info+= err_new
        
            if len(md.l_moved) > 0:
                err_info+= err_moved
        
            if len(md.l_topology_changed) > 0:
                err_info+= err_topology_changed

            if err_info:
                err_info = u"提交的模型和检测的模型不一致。\n请不要把模型P出去骗过检测，这样会对下游很多环节造成很大的麻烦！ \n" + err_info
            
            return err_info
    
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


