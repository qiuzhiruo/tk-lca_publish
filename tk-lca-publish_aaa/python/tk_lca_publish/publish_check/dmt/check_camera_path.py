# -*- coding:utf-8 -*-

import traceback

import os
import shutil
import nuke
import fn_common as fc

reload(fc)
import stereo.findStereoCamera as fsc

reload(fsc)


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查相机"
        self.description = u"如果使用了相机投射，则必须使用最新的相机文件"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            cams = fc.getAllNodes(node_type='Camera2', return_node=True, discard_isolated=True)
            latest_cam = fsc.findStereoCamera(self.dialog.entity['name'].lower(), self.dialog.project['name'].lower())
            if not isinstance(latest_cam, type('')):
                print 'There is no stereo camera for publish, ignored this check.'
                return ""

            old_cam_list = []
            for c in cams:
                if c.name().lower().startswith('camera_user'):
                    # ignore user camera
                    continue

                cam_full_name = c.fullName()
                if 'DMT_3D_Proj' not in str(cam_full_name):
                    # ignore camera out of DMT_3D_Proj_Sky group
                    continue

                cam_path = c['file'].value()
                if cam_path:
                    cam_path_shot = cam_path.split("/")[7]
                    latest_cam_shot = latest_cam.split("/")[7]
                    if cam_path_shot == latest_cam_shot:
                        if cam_path != latest_cam:
                            old_cam_list.append(cam_full_name)
                else:
                    continue

            if old_cam_list:
                return u"以下DMT使用的相机不是最新的版本，请先更新DMT内容·摄像机节点名称：\n" + str(old_cam_list)
            else:
                return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
