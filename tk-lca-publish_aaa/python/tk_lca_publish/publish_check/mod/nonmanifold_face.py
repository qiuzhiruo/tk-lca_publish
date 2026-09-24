# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.09
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
        self.check_name = u"检查 non-manifold (无法在一个平面上展开) 的面。"
        self.description = u"一般这几种情况会导致面无法展开：\n三个或以上的面共享一条棱;\n两个或以上的面通过一个点而不是棱连接；\n相邻的两个面，法线相反 。skip tag: skip_bad_face"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return
    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info

    @record_time(__file__)
    def run_check(self):
        try:
            l_bad_faces = []
            l_bad_vertex = []
            for asset_name in self.dialog.d_assets_info.keys():
                sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
                if 'skip_bad_face' in sg_info['tag_list']:
                    print 'skip nonmanifold_face check'
                    return ''

                root = self.dialog.d_assets_info[asset_name]['node']

                if root.fullPath() == '|master':
                    l_meshes = pm.listRelatives('|master|poly|hi', ad=True, type='mesh')
                    if pm.objExists('|master|shape'):
                        l_meshes.extend(pm.listRelatives('|master|shape', ad=True, type='mesh', path=True))
                else:
                    l_meshes = pm.listRelatives(root, ad=True, type='mesh')

                for n in l_meshes:
                    result = pm.polyInfo(n, nmv=True, nme=True )
                    if result:
                        l_bad_vertex.extend(result)
                        l_bad_faces.append(n)

            if len(l_bad_faces)>0:
                l_names = [n.name() for n in l_bad_faces]
                pm.select(l_bad_vertex, r=True)
                return u"发现 non-manifold 面:" + u" ".join(l_names)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
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


