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
import maya.cmds as cmds

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查节点重名。"
        self.description = u"在所有组下所有节点的命名是唯一的。\n另外模型和绑定场景内不能有名为 hair, cloth 的 shader，避免影响未来下游CFX的关键组 |master|hair, |master|cloth 命名。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            grps=['facial_modules_grp', "facial_controls_grp", "facial_skeletons_grp", 'facial_model_grp']
            err_msg = ''
            d_name = {}
            for grp in grps:
                #grp='Facial_model'
                l_nodes = pm.listRelatives(grp, ad=True, fullPath=True)
                for node in l_nodes:
                    #node = l_nodes[0]
                    node_name = node.name().split('|')[-1]
                    if not d_name.has_key(node_name):
                        d_name[node_name] = []

                    d_name[node_name].append(node.fullPath())

            for name, l_paths in d_name.iteritems():
                if len(l_paths) > 1:
                    err_msg += u'物体重名: ' + ' '.join(l_paths) + '\n'

                if err_msg != '':
                    return err_msg

                l_nodes = pm.ls('hair')
                for n in l_nodes:
                    if not hasattr(n, 'fullPath'):
                        return u"场景内有名为 hair 的 "+ n.type() +u" 节点。它会影响未来 CFX 的 |master|hair 组命名。\n请删除或重命名后再 publish。"

                l_nodes = pm.ls('cloth')
                for n in l_nodes:
                    if not hasattr(n, 'fullPath'):
                        return u"场景内有名为 cloth 的 "+ n.type() +u" 节点。它会影响未来 CFX 的 |master|cloth 组命名。\n请删除或重命名后再 publish。"

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


