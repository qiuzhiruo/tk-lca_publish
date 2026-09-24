# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.03
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
        self.check_name = u"重新排列组里的节点顺序。"
        self.description = u"将组内的 group, assembly, transform 和 其他节点分别按名称排序。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def get_node_type(self, node):
        node_type = pm.mel.eval('nodeType ' + node.name())
        if node_type != 'transform':
            if node_type == 'assemblyReference':
                return node_type
            else:
                return 'other'
        l_shapes = pm.listRelatives(node, children=True, shapes=True)
        if len(l_shapes) > 0:
            return 'transform'
        return 'group'


    def name_order(self, l_names):
        d_keys = {}
        for node_name in l_names:
            prefix = ''
            suffix = ''
            if node_name.endswith('_AR'):
                name = node_name[:-3]
                suffix = '_AR'
            else:
                name = node_name

            prefix = name.rstrip('0123456789')
            name_key = prefix + '+' + suffix
            if not d_keys.has_key(name_key):
                d_keys[name_key] = {}
        
            num = name[len(prefix):]
            if num.isdigit():
                num_key = int(num)
            else:
                num_key = -1
                
            if not d_keys[name_key].has_key(num_key):
                d_keys[name_key][num_key] = []
                
            d_keys[name_key][num_key].append(node_name)
        
        l_new_order = []
        for name_key in sorted(d_keys.keys()):
            for num_key in sorted(d_keys[name_key].keys()):
                for node_name in sorted(d_keys[name_key][num_key]):
                    l_new_order.append(node_name)

        return l_new_order


    def reorder_nodes(self, root_node):

        l_nodes = pm.listRelatives(root_node, children=True)
        l_node_types = [  'group', 'assemblyReference', 'transform', 'other' ]
        d_nodes = {'group':{}, 'assemblyReference':{}, 'transform':{}, 'other':{}}

        for n in l_nodes:
            node_type = self.get_node_type(n)
            node_name = n.name()
            d_nodes[node_type][node_name] = n

        for node_type in l_node_types:
            l_node_names = self.name_order(d_nodes[node_type].keys())
            for node_name in l_node_names:
                n = d_nodes[node_type][node_name]
                pm.reorder(n, back=True)
                
                if node_type == 'group' and not pm.referenceQuery(n, isNodeReferenced=True):
                    self.reorder_nodes(n)

    @record_time(__file__)
    def run_check(self):
        try:
            if pm.objExists('|master|asb'):
                self.reorder_nodes('|master|asb')
            elif pm.objExists('|master|poly'):
                if not self.dialog.mod_asset['sg_asset_type'] in ['chr', 'crd']:
                    self.reorder_nodes('|master|poly')
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


