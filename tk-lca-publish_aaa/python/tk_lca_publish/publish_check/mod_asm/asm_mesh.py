# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Huazhuo Yu
#
# Date: 2013.10
#
# Description: Check to see if too many (more than 5) faces are connected on a vertex.
#
########################################################################################

import traceback
import os
import maya.OpenMaya as om
import pymel.core as pm
import hashlib,sys
from xml.etree import ElementTree


# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查模型是否和父资产匹配。"
        self.description = u"检查asm资产的层级拓扑是否和shotgun父资产匹配，如果不匹配请重新获取最新版父资产模型。skip tag: skip_paternity"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info

    def get_mesh_md5(self, obj):
        v = obj.getVertices()
        v_str0 = '[' + ', '.join([str(i) for i in v[0]]) + ']'
        v_str1 = '[' + ', '.join([str(i) for i in v[1]]) + ']'
        topology = hashlib.md5(v_str0 + ' ' + v_str1).hexdigest()

        return topology

    def xml_to_dict(self, mesh_xml, root_node='|master|poly|hi|'):
        d_meshes = {}
        l_order = []
        tree = ElementTree.parse(mesh_xml)
        root = tree.getroot()
        l_meshes = root.getiterator("mesh")
        for mesh in l_meshes:
            full_path = mesh.attrib['name']
            if not root_node in full_path:
                continue
            mesh_name = full_path.split('|')[-1]
            topology = mesh.attrib['topology']
            d_meshes[mesh_name] = {'path': full_path, 'topology': topology}
            l_order.append(mesh_name)
        return d_meshes, l_order

    def check_mesh(self, mesh_xml, root_node='|master|poly|hi'):
        topo_error_list = []
        obj_error_list = []
        d_old_meshes, l_old_order = self.xml_to_dict(mesh_xml, root_node=root_node)
        d_new_meshes = {}
        l_new_mesh = pm.listRelatives(root_node, ad=True, type='mesh', noIntermediate=True)
        for i, mesh in enumerate(l_new_mesh):
            mesh_name = mesh.name().split('|')[-1]
            d_new_meshes[mesh_name] = ''

            if mesh_name in d_old_meshes.keys() and mesh.fullPath() == d_old_meshes[mesh_name]['path']:

                topology = self.get_mesh_md5(mesh)
                if topology != d_old_meshes[mesh_name]['topology']:
                    topo_error_list.append(mesh_name)
            
        for mesh_name in d_old_meshes.keys():
            if not pm.objExists(d_old_meshes[mesh_name]['path']):
                obj_error_list.append(mesh_name)

        return topo_error_list,obj_error_list

    def run_check(self):
        try:
            parent_list = self.dialog.sg.find('Asset', [['project', 'name_is', self.dialog.project['name'].lower()],
                                                        ['assets','name_is',self.dialog.entity['name']],
                                                        ['sg_asset_type','is','asm']],[ 'code','sg_asset_type'])

            for asset_name in self.dialog.d_assets_info.keys():
                if self.dialog.d_assets_info[asset_name]['type'] == 'chr':
                    sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
                    if 'skip_paternity' in sg_info['tag_list']:
                        print "skip_paternity"
                        return ''

            for parent in parent_list:

                parent_name=parent['code']
                parent_xml = '/mnt/proj/projects/{0}/asset/{2}/{1}/mod/publish/{1}.mod.model/mesh.xml'.format(
                        self.dialog.project['name'].lower(), parent_name,parent['sg_asset_type'])
                if sys.platform == 'win32':
                    parent_xml = 'Z:/projects/{0}/asset/{2}/{1}/mod/publish/{1}.mod.model/mesh.xml'.format(
                            self.dialog.project['name'].lower(), parent_name,parent['sg_asset_type'])

                if not os.path.isfile(parent_xml):
                    return u'没有找到 父资产xml文件 ： %s，请联系TD。' % parent_xml

                if not pm.objExists('|master|poly|hi'):
                    return u'没有找到 |master|poly|hi 组。'

                topo_error_list,obj_error_list = self.check_mesh(parent_xml)

                if len(topo_error_list) != 0:
                    return u'{0} 这些模型相比于父资产{1}有修改，请重新获取父资产。'.format(','.join(topo_error_list), parent_name)

                if len(obj_error_list) != 0:
                    return u'{0} 这些模型相比于父资产{1}有缺失，请重新获取父资产。'.format(','.join(obj_error_list), parent_name)


                print 'check pass',parent_xml
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
