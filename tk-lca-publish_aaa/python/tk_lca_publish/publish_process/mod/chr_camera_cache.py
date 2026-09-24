# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: Yu Hua Zhuo
#
# Date: 2017.7
#
# Description:
#
############################################


import os
import traceback
from xml.dom.minidom import Document
import pymel.core as pm
import maya.cmds as cmds
import shutil
from proc.function_running_time import record_time
try:
    cmds.loadPlugin('AbcExport', quiet=True)
except:
    pass

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出角色Turntable相机"
        self.description = u"导出角色Turntable相机，给下游环节使用。保证review相机一样。"
        return

    def get_version(self,out_path):
        if not os.path.exists(out_path):
            os.makedirs(out_path, 0777)
            os.chmod(out_path,0777)
        l_versions = sorted(os.listdir(out_path))
        l_mtl_v = [v for v in l_versions if v.startswith('v') and v[-3:].isdigit()]
        if len(l_mtl_v) == 0:
            version = 'v001'
        else:
            version = ('v%03d' % (int(l_mtl_v[-1][-3:]) + 1))
    
        return version
    
    
    def get_version_path(self):
        maya_file_name = pm.sceneName()
        pb_dir = os.path.join(os.path.dirname(maya_file_name), 'images/turntable')
        version = self.get_version(pb_dir)
        version_path = os.path.join(pb_dir, version)
        if os.path.isdir(version_path):
            shutil.rmtree(version_path)
        os.makedirs(version_path, 0777)
        os.chmod(version_path,0777)
        return version_path
    

    @record_time(__file__)
    def proceed(self):
        try:
            if not cmds.objExists('|turntable_cam|body_cam_group|body_cam|body_camShape'):
                print 'not find  body_cam ...'
                return ""

            if not cmds.objExists('|turntable_cam|head_cam_group|head_cam|head_camShape'):
                print 'not find  head_cam ...'
                return ""

            # export camera to publish
            asset = self.dialog.entity['name'].lower()
            version_dir = self.dialog.d_assets_info[asset]['version_dir']
            out_dir=version_dir+'/turntable_cam'

            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
                os.chmod(out_dir,0777)
            # set overscan 1
            pm.setAttr('head_camShape.overscan', lock=False)
            pm.setAttr('body_camShape.overscan', lock=False)
            pm.setAttr('head_camShape.overscan', 1)
            pm.setAttr('body_camShape.overscan', 1)
            pm.setAttr('head_camShape.overscan', lock=True)
            pm.setAttr('body_camShape.overscan', lock=True)
            #
            pm.AbcExport(j='-frameRange 1 1 -uvWrite -writeVisibility -dataFormat ogawa -root |turntable_cam|head_cam_group|head_cam -file '+out_dir+'/head_cam.abc')
            pm.AbcExport(j='-frameRange 1 1 -uvWrite -writeVisibility -dataFormat ogawa -root |turntable_cam|body_cam_group|body_cam -file '+out_dir+'/body_cam.abc')

            # export camera to work
            version_path = self.get_version_path()
            cam_path = version_path + '_cam.ma'
            pm.select(pm.listRelatives('turntable_cam', ad=1))
            

            pm.exportSelected(cam_path, force=True, options="v=0;", typ="mayaAscii")
            pm.AbcExport(
                j='-frameRange 1 1 -uvWrite -writeVisibility -dataFormat ogawa -root |turntable_cam|head_cam_group|head_cam -file ' + version_path + '/head_cam.abc')
            pm.AbcExport(
                j='-frameRange 1 1 -uvWrite -writeVisibility -dataFormat ogawa -root |turntable_cam|body_cam_group|body_cam -file ' + version_path + '/body_cam.abc')

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

