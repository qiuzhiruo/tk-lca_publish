# -*- coding:utf-8 -*-
__author__ = 'xiangquan'


import traceback
import os
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查与摄像机重名的节点'
        self.description = u'检查与摄像机重名的节点'
        self.auto_fix = True
        self.duty = u'自动修复'
        return

    def run_check(self):
        try:
            # check cam names
            cams = pm.listRelatives('cameras', children = True)
            cams2 = pm.ls('*_cam')
            cameras = list(set(cams).intersection(set(cams2)))


            cam_names = []
            self.dup_cams = []
            for camera in cameras:
                cam_name = camera.fullPath().rsplit('|', 1)[-1]
                cam_names.append(cam_name)
                all_cam_names = pm.ls(cam_name)
                if len(all_cam_names) > 1:
                    print all_cam_names
                    self.dup_cams.append(all_cam_names)

            self.dup_cam_rigs = []
            for cam_name in cam_names:
                cam_rigs = pm.ls(cam_name + '_rig:global_ctrl')
                if len(cam_rigs) > 1:
                    self.dup_cam_rigs.append(cam_rigs)
                    print cam_rigs

            msg = ''
            if self.dup_cams:
                msg = u'以下相机被重名了:\n'
                for dup_cam in self.dialog.dup_cams:
                    msg += str(dup_cam) + '\n'
                msg += '\n'

            if self.dup_cam_rigs:
                msg += u'以下相机rig被重名了:\n'
                for dup_cam_rig in self.dup_cam_rigs:
                    msg += str(dup_cam_rig) + '\n'
                msg += '\n'

            return msg
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        # e.g. [[nt.Transform(u'ALL_CAMERA|k50680_cam'), nt.Transform(u'cameras|k50680_cam')]]
        for dup_cam in self.dup_cams:
            i = 1
            for cam in dup_cam:
                if '|cameras|' not in cam.fullPath():
                    find_new_name = False
                    while not find_new_name:
                        new_name = cam.fullPath() + str(i)
                        i += 1
                        if not pm.objExists(new_name):
                            cam.rename(new_name)
                            find_new_name = True

        # e.g. [[nt.Transform(u'ALL_CAMERA|k50625_cam_rig:global_ctrl|k50625_cam_rig:global_ctrl'),
        #        nt.Transform(u'ALL_CAMERA|k50625_cam_rig:global_ctrl')] ]
        for dup_cam_rig in self.dup_cam_rigs:
            i = 1
            for cam_rig in dup_cam_rig:
                shape = cam_rig.getShape()
                if shape and shape.type() == 'nurbsCurve':
                    continue
                else:
                    find_new_name = False
                    while not find_new_name:
                        new_name = cam_rig.fullPath().replace(':', str(i) + '_')
                        i += 1
                        if not pm.objExists(new_name):
                            cam_rig.rename(new_name)
                            find_new_name = True

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

