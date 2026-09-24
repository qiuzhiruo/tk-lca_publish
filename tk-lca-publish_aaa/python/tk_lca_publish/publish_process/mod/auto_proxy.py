# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.06
#
# Description: 
#
############################################

import os
import traceback
import math
import pymel.core as pm
from proc.function_running_time import record_time

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"如果没有proxy代理模，根据高模自动输出一个。"
        self.description = u"如果没有proxy代理模，根据高模自动输出一个。"
        return


    def get_reduced_cnt(self, n):
        if n <= 6:
            return float(n)
        if 6< n and n < 1000:
            return math.log(n+53)*50 - 197.87
        else:
            return 150 + (n - 1000)/20.0

    def get_bbox(self, n):
        bbox = n.getBoundingBox()
        return [abs(bbox[0][0] - bbox[1][0]), abs(bbox[0][1] - bbox[1][1]), abs(bbox[0][2] - bbox[1][2])]

    def get_mesh_count(self, root_node):
        if not pm.objExists(root_node):
            return 0

        l_meshes = pm.listRelatives(root_node, ad=True, type='mesh')
        if len(l_meshes) == 0:
            return 0

        pm.select(l_meshes, r=True)
        cnt = pm.polyEvaluate(f=True)
        pm.select(cl=True)
        return cnt

    def get_size_penalty(self, n):
        mesh_bbox = self.get_bbox(n)
        size_rate = []
        for j in range(3):
            if self.proxy_bbox[j]==0:
                size_rate.append(0.000001)
            else:
                size_rate.append(mesh_bbox[j]/self.proxy_bbox[j])
        size_rate.sort()

        if size_rate[1] < 0.01:
            size_factor = size_rate[1]*20 + 0.1
        elif size_rate[1] < 0.1:
            size_factor = (size_rate[1]-0.01)*7.777 + 0.3
        else:
            size_factor = 1.0

        return size_factor

    @record_time(__file__)
    def proceed(self):
        try:

            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                node_name = self.dialog.d_assets_info[asset_name]['node_name']
                asset_type = self.dialog.d_assets_info[asset_name]['type']

                if asset_type == 'chr' and self.dialog.step['name'] == 'rig':
                    continue

                # make a master if necessary
                if self.dialog.d_assets_info[asset_name]['parent']:
                    pm.parent(root, world=True)

                if node_name != 'master':
                    root.rename('master')

                # Create proxy res
                if not pm.objExists('|master|poly|proxy'):

                    n = pm.duplicate('|master|poly|hi', rr=True)[0]
                    n.rename('proxy')

                    pm.addAttr(n, shortName = 'ap', longName = 'auto_proxy', dt="string")
                    meshs=pm.listRelatives(root,ad=True, type='mesh')

                    if asset_type!='env' and pm.polyEvaluate(meshs, f=True)<100000 and len(meshs)<500:
                        self.proxy_bbox = self.get_bbox(n)

                        l_meshes = pm.listRelatives(n, ad=True, type='mesh')
                        for i in range(len(l_meshes)):
                            mesh = l_meshes[i]
                            mesh_cnt = pm.polyEvaluate(mesh, f=True)
                            size_factor = self.get_size_penalty(mesh.getParent())
                            new_cnt = self.get_reduced_cnt(mesh_cnt) * size_factor
                            if int(math.ceil(new_cnt)) < mesh_cnt:
                                rate = (1.0 - float(new_cnt)/mesh_cnt) * 100.0
                                pm.polyReduce(mesh, ver=1, p=rate, shp=0, symmetryTolerance=0.01, keepQuadsWeight=1, vertexMapName="", replaceOriginal=1, cachingReduce=1, ch=1)
                                mesh_cnt2 = pm.polyEvaluate(mesh, f=True)
                                pm.select(mesh, r=True)
                                pm.mel.eval('DeleteAllHistory;')
                                print i, 'of', len(l_meshes), mesh.name().split('|')[-1], mesh_cnt, '>', mesh_cnt2, '('+str(int(rate))+'%)'

                # Create proxy lock
                else:
                    proxy_node=pm.PyNode('|master|poly|proxy')
                    if not proxy_node.hasAttr('mod_proxy'):
                        proxy_node.addAttr('mod_proxy')


                #updata poly low cunt face num
                lo_cnt = self.get_mesh_count('|master|poly|proxy')
                self.dialog.sg.update('Asset', self.dialog.entity['id'], { 'sg_poly_count_lo':lo_cnt })

                # recovery root node
                if self.dialog.d_assets_info[asset_name]['parent']:
                    pm.parent(root, self.dialog.d_assets_info[asset_name]['parent'])

                if node_name != 'master':
                    root.rename(node_name)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


