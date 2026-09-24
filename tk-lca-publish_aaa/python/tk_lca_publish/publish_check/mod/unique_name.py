# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: 
#
########################################################################################

import traceback
import pymel.core as pm
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查节点重名。"
        self.description = u"在master组下所有节点的命名是唯一的。\n另外模型和绑定场景内不能有名为 hair, cloth 的 shader，避免影响未来下游CFX的关键组 |master|hair, |master|cloth 命名。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            err_msg = ''
            
            
            # Zero tolerance
            for key_word in ['hair', 'cloth']:
                l_nodes = pm.ls(key_word)
                if len(l_nodes) > 0:
                    err_msg+= u"场景内有名为 "+ l_nodes[0].nodeName() +u" 的 "+ l_nodes[0].type() +u" 节点。它会影响未来 CFX 的节点命名。\n请删除或重命名后再 publish。"
            
            for key_word in ['persp', 'top','front','side']:
                l_nodes = pm.ls(key_word)
                if len(l_nodes) > 1:
                    for node in l_nodes:
                        if node.fullPath() not in ['|persp', '|top','|front','|side']:
                            err_msg+= u"场景内有名为 "+ l_nodes[0].nodeName() +u" 的 "+ l_nodes[0].type() +u" 节点。它会影响未来 RIG 的节点命名。\n请删除或重命名后再 publish。"


            # One tolerance
            if len(self.dialog.d_assets_info.keys()) == 1:
                for key_word in ['master', 'poly', 'hi', 'md', 'lo', 'proxy', 'shape', 'misc']:
                    l_nodes = pm.ls(key_word)
                    if len(l_nodes) > 1:
                        l_node_names = [n.name() for n in l_nodes]
                        err_msg+= u"场景内有多个名为 " + key_word + u"的节点：" + u', '.join(l_node_names)

            

            l_res = ['hi', 'md', 'lo', 'proxy', 'misc']

            d_name = {}
            for res_str in l_res:
                if not pm.objExists(res_str):
                    continue
                res=pm.PyNode(res_str)
                node_list=pm.listRelatives(res, ad=True, fullPath=True)
                if pm.objExists('shape'):
                    node_list.extend(pm.listRelatives('shape', ad=True, fullPath=True))
                for node in node_list:
                    node_name = res.fullPath() + ': ' + node.name().split('|')[-1]
                    if not d_name.has_key(node_name):
                        d_name[node_name] = []
                    full_path_list = []
                    if not node_name.endswith('mesh_grp'):
                        full_path_list.append(node.fullPath())
                    d_name[node_name] += list(set(full_path_list))
            error_list = []
            for name, l_paths in d_name.iteritems():
                if len(l_paths) > 1:
                    err_msg += u'物体重名: ' + ' '.join(l_paths) + '\n'
                    error_list.append(l_paths)

            if err_msg != '':
                if error_list:
                    pm.select(error_list)
                return err_msg

            return err_msg

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


