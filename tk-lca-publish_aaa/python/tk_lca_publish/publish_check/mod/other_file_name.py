# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check shtogun data
#
############################################

import traceback

import os
import sys
import re
import glob
import pymel.core as pm
import maya.api.OpenMaya as om
import hashlib
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的额外文件的路径和命名。"
        self.description = u"必须有一个文件有hi.abc;提交的预览文件名由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成，英文字母全小写。\n文件路径所在的各级文件夹命名不能有中文和空格 。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return
    
    
    
    def get_topo(self,node):
        
        if pm.polyEvaluate(node, face=True) == 0:
            topology = hashlib.md5(' ').hexdigest()
        else:
            sl = om.MSelectionList()
            sl.add(node.fullPath())
            mesh_dag = sl.getDagPath(0)
            mesh_mfn = om.MFnMesh(mesh_dag)
            v = mesh_mfn.getVertices()
            v_str0 = '[' + ', '.join([str(i) for i in v[0]]) + ']'
            v_str1 = '[' + ', '.join([str(i) for i in v[1]]) + ']'
            topology = hashlib.md5(v_str0 + ' ' + v_str1).hexdigest()

        return topology
        
        
    
    def check_topo(self,ref_node,real_path):
        orgin_node = pm.PyNode(real_path)
        orgin_topo = self.get_topo(orgin_node)
        
        ref_topo = self.get_topo(ref_node)
        
        if orgin_topo==ref_topo:
            return True
        else:
            return False
    
    
    def check_dynamic(self,dynamic_list):
        error_str = ''
        
        if self.dialog.export_dynamic:
            return
        
        for dynamic_file in dynamic_list:
            res = dynamic_file.split('.')[-3]
    
            ref_nodes = pm.createReference(dynamic_file, returnNewNodes=1, namespace='check_dynamic')
    
            for ref_node in ref_nodes:
                if ref_node.type() == 'mesh':
                    real_path = '|master|poly|' + res + ref_node.fullPath().replace('check_dynamic:', '')
                    if not pm.objExists(real_path):
                        error_str+=u'\n动态层级不匹配  '+real_path

                    elif not self.check_topo(ref_node,real_path):
                        error_str += u'\n动态拓扑不匹配  ' + real_path
                        
            ref_nodes[0].referenceFile().remove()
        return error_str


    @record_time(__file__)
    def run_check(self):

        try:
            work_dynamic_file_list = [self.dialog.w_publish_file.listWidget_dy.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_dy.count())]
            print 'work_dynamic_file_list:'
            print work_dynamic_file_list
            dynamic_list = []
            if len(work_dynamic_file_list) != 0:


                p1 = re.compile("[\w\.-]*$")
                p2 = re.compile("[\w\.]*$")
                hi_abc=False
                
                for file_path_qtstr in work_dynamic_file_list:
                    file_path = str(file_path_qtstr)
                    if '.dynamic.hi.' in file_path:
                        hi_abc=True

                    if not os.path.isfile(file_path):
                        return u"找不到这个文件:\n  " + file_path

                    tokens = file_path.replace(":", "\\").replace("/", "\\").split("\\")
                    for token in tokens[:-1]:
                        if not p1.match(token):
                            return u"各级文件夹需要由a-z的字母，0-9数字，下划线\"_\"，中划线\"-\"和点\".\"组成:\n  " + "\"" + token + "\" in " + file_path

                    if not p2.match(tokens[-1]):
                        return u"文件名需要由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成:\n  " + tokens[-1]

                    if tokens[-1] != tokens[-1].lower():
                        return u"\n文件名必须全小写:" + tokens[-1]

                    if not '.' in tokens[-1]:
                        return u"\n文件名必须有扩展名:" + tokens[-1]
                    dynamic_list.append(file_path)
                    
                if hi_abc==False:
                    return u"\n必须有包含 高模的动态 (.dynamic.hi.###_###.abc) 的文件."
            
            if dynamic_list:
                check_str = self.check_dynamic(dynamic_list)
                if check_str:
                    return check_str

            mod_asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]],['tags','code','sg_asset_type'])
            tags=[t['name'] for t in mod_asset['tags']]
            print 'mod_asset tags : ',mod_asset,tags


            if 'zb' not in tags:
                return ""

            zbrush_glob_str = 'Z:/projects/{0}/asset/{1}/{2}/mod/publish/*/zbrush/*.ZTL'.format(
                    self.dialog.project['name'].lower(), mod_asset['sg_asset_type'], mod_asset['code'])

            if sys.platform.startswith('linux'):
                zbrush_glob_str = zbrush_glob_str.replace('Z:/', '/mnt/proj/')

            print 'zbrush_glob_str :',zbrush_glob_str
            old_zb_files=glob.glob(zbrush_glob_str)

            if old_zb_files :
                print 'old_zb_files : ',old_zb_files
                return ""


            work_zb_file_list = [self.dialog.w_publish_file.listWidget_zb.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_zb.count())]
            work_zb_view_file_list = [self.dialog.w_publish_file.listWidget_zb_view.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_zb_view.count())]


            if len(work_zb_file_list) == 0 or len(work_zb_view_file_list) == 0:
                return u"资产有zb的标签所以必须提交zb文件和预览图"

            return ""
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


