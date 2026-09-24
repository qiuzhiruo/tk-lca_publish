# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2017.07
#
# Description: For each group (not a shape-parent transform node) under <res>/mesh_grp, 
#              there must be more than one transform nodes under it. 
#
########################################################################################
import sys
import os
import traceback
import pymel.core as pm
from xml.etree import ElementTree
from proc.function_running_time import record_time
# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查只有一个子组的父组。"
        self.description = u"在 hi/md/lo/proxy 或者 mesh_grp 这样的组下的其他组，父组下如果还有子组，子组不应该少于一个，否则父组是多余的。skip tag: skip_no_standalone_group"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info

    def get_one_group(self,node,error_list=None):
        if error_list==None:
            error_list=[]
        node_list=pm.listRelatives(node, ad=True, path=True,type='transform')
        for node in node_list:
            if node.name() in ['hint_grp', 'attach_grp', 'cloth_grp']:
                continue
            n_list=pm.listRelatives(node,type='transform')
            if len(n_list)==1:
                error_list.append(node)
            elif len(n_list)>1:
                for n in n_list:
                    if n not in node_list:
                        error_list.extend(self.get_one_group(n,error_list))

        return error_list

    def get_version_log(self):
        tag=None
        l_attrs = pm.listAttr('|master')
        if ('modVersion' in l_attrs and 'modPath' in l_attrs):
            mod_path = pm.getAttr('|master.modPath').replace('\\', '/')
            log_xml = os.path.join(os.path.dirname(mod_path) , 'version_log.xml')
            if sys.platform.startswith('linux'):
                log_xml = log_xml.replace('Z:/', '/mnt/proj/')
            else:
                log_xml = log_xml.replace( '/mnt/proj/','Z:/')
            tree = ElementTree.parse(log_xml)
            root = tree.getroot()
            tag = root.getiterator("Tag")[0].attrib['value']

        return tag


    @record_time(__file__)
    def run_check(self):
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
                if self.dialog.d_assets_info[asset_name]['type'] == 'chr':
                    if 'skip_no_standalone_group' in sg_info['tag_list']:
                        return ''
                # skip face pass , crd face pass and fur pass
                if self.dialog.d_assets_info[asset_name]['type'] in ['crd'] and 'crd_face_pass' in sg_info['tag_list']:
                    return ''
                if sg_info['tag_list'] and 'fur_pass' in sg_info['tag_list']:
                    return ''
                face_pass_grp = pm.ls('|master|shape|face_pass_grp')
                if face_pass_grp:
                    return ''

                root = self.dialog.d_assets_info[asset_name]['node']
                if not pm.objExists(root):
                    return u'没有找到 '+root.name()

                grp_exception = ['hi', 'md', 'lo','proxy']
                if self.dialog.usd:
                    grp_exception.append('mesh_grp')

                l_one_group_list=[]
                if not self.dialog.version_tag == u"粗模":
                    try:
                        asset_old_version_tag = self.get_version_log()
                    except:
                        break
                    if asset_old_version_tag == u"粗模" or self.dialog.version_num=='001':
                        l_groups = self.get_one_group(root.name() + '|poly')
                        l_one_group = [n for n in l_groups if not n.nodeName() in grp_exception]
                        l_one_group_list=list(set([n.name() for n in l_one_group]))

                if len(l_one_group_list) > 0:
                   return u"模型组中不能有单层级的组: " + ' '.join(l_one_group_list) + '\n skip tag: skip_no_standalone_group'

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']

                if not pm.objExists(root):
                    return u'没有找到 '+root.name()

                grp_exception = ['hi', 'md', 'lo']
                if self.dialog.usd:
                    grp_exception.append('mesh_grp')

                if not self.dialog.version_tag == u"粗模":
                    try:
                        asset_old_version_tag = self.get_version_log()
                    except:
                        break
                    if asset_old_version_tag == u"粗模" or self.dialog.version_num=='001':
                        l_groups = self.get_one_group(root.name() + '|poly')
                        l_one_group = [n for n in l_groups if not n.nodeName() in grp_exception]

                for n in l_one_group:
                    pm.ungroup(n.name())

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


