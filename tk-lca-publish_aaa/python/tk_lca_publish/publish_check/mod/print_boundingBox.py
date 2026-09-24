# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: Check to see if any vertice are overlapping to each other.
#
########################################################################################

import traceback
import os
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as om
import production.pipeline.lcProdProj as lcp
import re
import sys
from xml.etree import ElementTree
from proc.function_running_time import record_time


# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = self.get_asset_boundingBox()
        self.description = u"输出资产的长宽高，给制作人员参考判断。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def get_asset_boundingBox(self):
        try:
            hi = pm.PyNode('master|poly|hi')
            (hi_min, hi_max) = hi.boundingBox()
            x = hi_max[0] - hi_min[0]
            y = hi_max[1] - hi_min[1]
            z = hi_max[2] - hi_min[2]

            result = u'当前资产三围 X：{0}   Y：{1}   Z：{2}'.format("%.4f" % x, "%.4f" % y, "%.4f" % z)
            return result
        except:
            return u"显示资产的长宽高（可忽略）"

    def xml_to_bbox(self, mesh_xml):
        tree = ElementTree.parse(mesh_xml)
        root = tree.getroot()
        l_meshes = root.getiterator("instance")
        attr_list=['maxx','maxy','maxz','minx','miny','minz']
        for mesh in l_meshes:
            bbox_attr = mesh.getiterator('bounds')[0].attrib
            bbox_list = [bbox_attr[k] for k in attr_list]
            return bbox_list
        return ''

    @record_time(__file__)
    def run_check(self):
        try:
            l_attrs = pm.listAttr('|master')
            if not ('modVersion' in l_attrs and 'modPath' in l_attrs):
                print u"没有找到 Mod Version 和 Mod Path 属性，无法对比模型大小位移。"
                return ''

            mod_version = pm.getAttr('|master.modVersion')
            mod_path = pm.getAttr('|master.modPath').replace('\\', '/')
            assert_name = os.path.basename(mod_path.split('.')[0])
            if mod_version == '000':
                return ""
            mesh_xml = os.path.join(os.path.dirname(mod_path) , 'scene_graph_xml', assert_name + '.xml')
            if sys.platform.startswith('linux'):
                mesh_xml = mesh_xml.replace('Z:/', '/mnt/proj/')

            if not os.path.isfile(mesh_xml):
                print u"没有找到模型对应的 xml 文件: " + mesh_xml
                return ''

            old_bbox = self.xml_to_bbox(mesh_xml)
            if old_bbox == '':
                print u'没有找到上一版本的boundingbox'
                return ''

            hi = pm.PyNode('master|poly|hi')
            (hi_min, hi_max) = hi.boundingBox()
            hi_min=[float(h) for h in hi_min]
            hi_max=[float(h) for h in hi_max]
            hi_max.extend(hi_min)

            mistake_num = 0
            for i in range(6):
                mistake = float(hi_max[i]) - float(old_bbox[i])
                mistake_num += abs(mistake)

            if mistake_num > 50:
                hi_max_str=["%.1f" % x for x in hi_max]
                error_tex=u'上一版本：{0} 此版本 {1}'.format(u''.join(str(old_bbox)),u''.join(str(hi_max_str)))
                return u'BoundingBox与上一版本相差过大，如果是有意而为且对下游影响不大请忽略此检查。 '+error_tex

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
