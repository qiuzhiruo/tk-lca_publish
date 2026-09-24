# -*- coding:utf-8 -*-

__author__ = 'xiangquan'

import os
import traceback
import shutil
import pymel.core as pm

IGNORE_LIST = ['FreeBlockCam', 'top_pb_cam']

# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u'删除assets|lay中无用的camera'
        self.description = u'Downstream时, 删除assets|lay下，除了FreeBlockCam和top_pb_cam之外的普通和立体相机'
        return
    
    def proceed(self):
        check_root = 'assets|lay'
        try:
            stereoCams = pm.listRelatives(check_root, allDescendents = True, type = 'stereoRigTransform')
            del_cam_list = stereoCams
            stereoCams_relatives = []
            for stereCam in stereoCams:
                stereoCams_relatives.extend(pm.ls(stereCam, allPaths = True, dag = True))
            
            children = pm.listRelatives(check_root, allDescendents = True, type = 'camera')
            for child in children:
                if child in stereoCams_relatives:
                    continue
                parent = pm.listRelatives(child, parent = True)[0]
                if self.check_light_camera_shape(parent):
                    if pm.lockNode(parent, query=True)[0]:
                        pm.lockNode(parent, lock=False)
                    pm.delete(child)
                    continue
                if str(parent) in IGNORE_LIST:
                    continue
                if pm.lockNode(parent, query = True)[0]:
                    pm.lockNode(parent, lock = False)
                elif pm.lockNode(child, query = True)[0]:
                    pm.lockNode(child, lock = False)
                del_cam_list.append(parent)
            
            del_cam_list = list(set(del_cam_list))
            pm.delete(del_cam_list)
            print 'Removing ', str([str(del_cam) for del_cam in del_cam_list])
            return ""
        except:
            return traceback.format_exc()

    # 删除，灯光，沿选定对象观看时生成的相机shape
    def check_light_camera_shape(self, parent):
        n = 0
        shapes = pm.listRelatives(parent, s=1)
        if shapes and len(shapes) >= 2:
            for s in shapes:
                if 'Light' in s.type():
                    n = 1
                    break
        return n

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
