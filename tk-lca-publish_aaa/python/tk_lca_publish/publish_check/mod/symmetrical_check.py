# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yu HuaZhuo
#
# Date: 2017.09
#

########################################################################################
import sys
import os
import traceback
import pymel.core as pm
import maya.cmds as mc
import maya.OpenMaya as om
from xml.etree import ElementTree
import maya.mel as mel
from proc.function_running_time import record_time


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查body是否形状对称"
        self.description = u"检查body是否形状对称(tag:'asymm'）"
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
            if self.dialog.version_tag == u"粗模":
                return ''
            for asset_name in self.dialog.d_assets_info.keys():
                if self.dialog.d_assets_info[asset_name]['type'] == 'chr':
                    #  find tag: asymm
                    sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
                    if 'asymm' in sg_info['tag_list']:
                        return ''
                    # pm.select('hi|mesh_grp|skin*|body_geo')
                    # mel.eval('source "%s/tools/mod/model_checks/abSymMesh_new.mel"' % os.environ["LC_TOOLSET"])
                    # output = mel.eval('abSymCtl(\"favBn\");')

                    mobj = pm.PyNode('hi|mesh_grp|skin*|body_geo').__apimobject__()
                    iter = om.MItMeshVertex(mobj)
                    l_dict = {}
                    l_dict_mirror = {}
                    r_dict = {}
                    r_dict_mirror = {}
                    bad_points = []
                    while not iter.isDone():
                        index = iter.index()
                        if 'e' in str(iter.position().x):
                            pos_x = 0.0
                        else:
                            pos_x = float(
                                str(iter.position().x).split('.')[0] + '.' + str(iter.position().x).split('.')[1][:6])
                        if 'e' in str(iter.position().y):
                            pos_y = 0.0
                        else:
                            pos_y = float(
                                str(iter.position().y).split('.')[0] + '.' + str(iter.position().y).split('.')[1][:6])
                        if 'e' in str(iter.position().z):
                            pos_z = 0.0
                        else:
                            pos_z = float(
                                str(iter.position().z).split('.')[0] + '.' + str(iter.position().z).split('.')[1][:6])
                        if pos_x != 0.0 and pos_x > 0:
                            r_dict[index] = [pos_x, pos_y, pos_z]
                            r_dict_mirror[index] = [-pos_x, pos_y, pos_z]
                        elif pos_x != 0.0 and pos_x < 0:
                            l_dict[index] = [pos_x, pos_y, pos_z]
                            l_dict_mirror[index] = [-pos_x, pos_y, pos_z]
                        iter.next()

                    for mirror_point in list(l_dict_mirror.keys()):
                        if l_dict_mirror[mirror_point] in r_dict.values():
                            l_dict_mirror.pop(mirror_point)
                    for mirror_point in list(r_dict_mirror.keys()):
                        if r_dict_mirror[mirror_point] in l_dict.values():
                            r_dict_mirror.pop(mirror_point)


                    def compare_coordinates(co1,co2):
                        [x1,y1,z1]=co1
                        [x2,y2,z2]=co2
                        if abs(-x2-x1)<=0.001 and abs(y2-y1)<=0.0001 and abs(z2-z1)<=0.0001:
                            return True
                        else:
                            return False


                    for i in list(l_dict_mirror.keys()):
                        for j in list(r_dict_mirror.keys()):
                            if compare_coordinates(l_dict_mirror[i],r_dict_mirror[j]) is True:
                                r_dict_mirror.pop(j)
                    for index in r_dict_mirror:
                        bad_points.append(index)

                    # Is ther a TD check mark?
                    if pm.objExists('td_name_check'):
                        n = pm.PyNode('td_name_check')
                        if n.hasAttr('asset') and n.getAttr('asset') == self.dialog.entity['name']:
                            return ""

                    # if output > 1:
                    #     return u"body_geo 形状不对称"

                    if bad_points:
                        mc.select(cl=1)
                        for p in bad_points:
                            mc.select('body_geo.vtx[{}]'.format(p), add=1)
                        return u"body_geo 形状不对称"

            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            return
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
