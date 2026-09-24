# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: No referenced nodes under |master.
#
########################################################################################

import traceback
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"资产里没有referenced节点。"
        self.description = u"有时候资产里会reference进来一些次级文件，比如角色资产reference一个独立制作的头绑定。这些reference在publish之前必须import进来。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:

            if not pm.general.objExists('|master'):
                return u'没有找到 |master 组。'

            l_nodes = pm.general.listRelatives('|master', ad=True, fullPath=True)
            l_ref_nodes = []

            dept = self.dialog.step['name']
            mod_publish_dir = self.dialog.publish_root.replace('/'+dept+'/', '/mod/')

            for node in l_nodes:
                if pm.system.referenceQuery(node, isNodeReferenced=True):
                    file_path = pm.referenceQuery('|master', filename =True)
                    if not file_path.startswith(mod_publish_dir):
                        l_ref_nodes.append(node)

            if len(l_ref_nodes) > 0:
                name_str = ', '.join([node.name() for node in l_ref_nodes])
                pm.general.select(l_ref_nodes, r=True )
                return u'|master 之下有非法的 reference的节点: '+name_str + u'。'

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            if not pm.general.objExists('|master'):
                return u'没有找到 |master 组。'

            l_nodes = pm.general.listRelatives('|master', ad=True, fullPath=True)
            l_ref_files = []

            for node in l_nodes:
                if pm.system.referenceQuery(node, isNodeReferenced=True):
                    file_path = pm.system.referenceQuery(node, filename=True)
                    l_ref_files.append(file_path)

            l_ref_files = list(set(l_ref_files))

            for file_path in l_ref_files:
                r = pm.system.loadReference(file_path)
                r.importContents(removeNamespace=True)

            return ''

        except:
            return traceback.format_exc()




    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



