# -*- coding:utf-8 -*-

import os
import traceback
import math
import shutil
import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds

try:
    cmds.loadPlugin('AbcExport', quiet=True)
except:
    pass

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"创建背景天空球和背景圆柱体"
        self.description = u"创建背景天空球和背景圆柱体"
        return

    def bounding_info(self, bounding):
        x_rad = pow(bounding[1][0] - bounding[0][0], 2)
        y_rad = pow(bounding[1][1] - bounding[0][1], 2)
        z_rad = pow(bounding[1][2] - bounding[0][2], 2)
        radius = math.sqrt(x_rad + y_rad + z_rad) * 1.2
        center = bounding.center()
        return radius, center

    def proceed(self):
        try:
            cache_dir = self.dialog.version_dir + '/dmt_cache'
            if not os.path.isdir(cache_dir):
                os.makedirs(cache_dir)
            master_node = pm.PyNode('master')
            bounding = master_node.getBoundingBox()

            radius, center = self.bounding_info(bounding)
            if cmds.lockNode('initialShadingGroup',q=1,lu=1):
                cmds.lockNode('initialShadingGroup', l=0, lu=0)
            env_ball = pm.polySphere(n='env_sphere', r=radius, sa=50, sh=50)
            pm.xform(env_ball[0], t=center)

            env_cyl = pm.polyCylinder(n='env_cylinder', r=radius / 2, h=radius, rcp=False, sa=50)
            pm.delete([env_cyl[0].name() + '.f[50]', env_cyl[0].name() + '.f[51]'])
            pm.xform(env_cyl[0], t=center)

            agvrs = "-frameRange 1 1 -uvWrite -worldSpace -dataFormat ogawa " + \
                    "-root |env_sphere -file %s" % (cache_dir + '/env_sphere.abc')

            agvrs_b = "-frameRange 1 1 -uvWrite -worldSpace -dataFormat ogawa " + \
                      "-root |env_cylinder -file %s" % (cache_dir + '/env_cylinder.abc')
            mel.eval("AbcExport -verbose -j \"%s\"" % agvrs)
            mel.eval("AbcExport -verbose -j \"%s\"" % agvrs_b)

            pm.delete(env_ball)
            pm.delete(env_cyl)
        except:
            return traceback.format_exc()
        return ""

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description