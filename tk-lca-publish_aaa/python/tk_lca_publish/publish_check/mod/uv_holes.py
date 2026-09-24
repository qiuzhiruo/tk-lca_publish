# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.09
#
# Description: 
#
########################################################################################

import traceback
import pymel.core as pm
import time
import maya.cmds as cmds
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"如果有UV，必须覆盖所有的面。"
        self.description = u"mesh节点可以没有UV；但如果有UV，所有face都要有UV 。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    # 模型的第一套uvset的名字必须是map1，这个函数就是更改uvset的名字
    def rename_uvSet(self):
        mesh_list = cmds.ls(type="mesh")
        for geo in mesh_list:
            f_cnt = pm.polyEvaluate(geo, face=True)
            if f_cnt == 0:
                continue
            cmds.select(geo, r=True)
            geo_uvSet = cmds.polyUVSet(geo, allUVSets=True, q=True)

            if len(geo_uvSet) > 1 and geo_uvSet[0] != "map1":
                t1 = time.gmtime()
                number = int(time.strftime("%Y%m%d%H%M%S", t1))
                # 给出错的uvset名字更改一个任意的名字
                for set_Name in geo_uvSet:
                    cmds.polyUVSet(rename=True, newUVSet='map' + str(number), uvSet=set_Name)
                    number += 1
                number_map = 1
                geo_uv = cmds.polyUVSet(geo, allUVSets=True, q=True)
                # 给uvset更改正确的名字 如 map1   map2   map3
                for s_Name in geo_uv:
                    cmds.polyUVSet(rename=True, newUVSet='map' + str(number_map), uvSet=s_Name)
                    number_map += 1

                continue

            if geo_uvSet[0] != "map1" and len(geo_uvSet) == 1:
                cmds.polyUVSet(rename=True, newUVSet='map1', uvSet=geo_uvSet[0])


    @record_time(__file__)
    def run_check(self):
        try:
            self.l_uv_holes = []
            self.rename_uvSet()
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                l_meshes = pm.listRelatives(root, ad=True, type='mesh')
        
                for n in l_meshes:
                    f_cnt = pm.polyEvaluate(n, face=True)
                    if f_cnt<2:
                        continue
                    f_str = '.f[0:%d]' % (f_cnt-1)
                    
                    uvset_list = pm.polyUVSet(n, allUVSets=True, q=True)
                    uvset_list.reverse()
                    for uvset in uvset_list:
                        if uvset != 'map1':
                            try:
                                pm.polyUVSet(n, d=True, uvSet=uvset)
                            except Exception as e:
                                print e
                                return u'%s uvset未能被删除，请检查其是否为默认的uvset并手动删除，注意场景中应只包含map1这个uvset' % uvset
                        pm.polyUVSet(n, currentUVSet=True, uvSet=uvset)
                        uv_covered = pm.polyListComponentConversion(n.name()+'.map[*]', fromUV=True, toFace=True)
                        if not (len(uv_covered) == 0 or (uv_covered[0].endswith(f_str))):
                            pm.select(uv_covered, r=True)
                            pm.mel.eval('InvertSelection;')
                            uv_error_dict = {'node':n,'uvset':uvset,'face':pm.ls(sl=True)}
                            
                            self.l_uv_holes.append(uv_error_dict)
                            

            if len(self.l_uv_holes) >0:
                pm.select(cl=1)
                error_str = u"没有 uv 的面: \n"
                for uv_d in self.l_uv_holes:
                    print 'uv_d : ', uv_d
                    error_str += 'mesh :' + str(uv_d['node']) +'uvset :' + uv_d['uvset'] +  str(uv_d['face']) + '\n'
                    pm.select(uv_d['face'], add=1)
                    
                return error_str

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            for uv_d in self.l_uv_holes:
                
                pm.polyUVSet(uv_d['node'], currentUVSet=True, uvSet=uv_d['uvset'])
                pm.select(uv_d['face'])
                uv_proj = pm.polyProjection(uv_d['node'].f, ch=1, type='Spherical', ibd=True, sf=True)
                if uv_proj:
                    pm.setAttr(uv_proj[0]+ '.rotateX', 45)
                    pm.setAttr(uv_proj[0]+ '.rotateY', 45)
                    pm.setAttr(uv_proj[0]+ '.rotateZ', 45)
                    pm.setAttr(uv_proj[0]+ '.imageScaleU', 0.1)
                    pm.setAttr(uv_proj[0]+ '.imageScaleV', 0.1)
                    

                pm.mel.eval('DeleteAllHistory;')
                pm.select(cl=True)
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


