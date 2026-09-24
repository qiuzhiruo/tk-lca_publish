# -*- coding:utf-8 -*-

import traceback

import os
import shutil
import nuke
import fn_common as fc
reload(fc)

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查投射相机是否正确"
        self.description = u"如果投射内容是背景，并且有多个立体相机，那么必须使用最远处的相机"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            cams = fc.getAllNodes(node_type='Camera2', return_node=True, discard_isolated=True)

            for c in cams:
                if c.name().lower().startswith('camera_user'):
                    # ignore user camera
                    continue
                namespace_grp = c.fullName().split('.')
                if len(namespace_grp) > 1:
                    if 'near' in namespace_grp[0].lower() or 'middle' in namespace_grp[0].lower():
                        # ignore near or middle projection
                        continue
                names = c['fbx_node_name'].value().split(' ')
                index = int( names[0].strip().replace('{','').replace('}','') )
                values = names[1:]
                if len(values)<=3 or index==0:
                    # this is not a multi-rig stereo camera, or the current camera is center, ignore the check
                    continue
                # determine the projection camera
                proj_cam = ''
                cam_join = ','.join(values)
                if '_Far_' in cam_join:
                    proj_cam = 'RenderStereoCam_Far_Grp'
                elif 'RenderStereoCam_Grp' in cam_join:
                    proj_cam = 'RenderStereoCam_Grp'
                else:
                    return c.name()+u": 投射用的相机不规范，请检查"
                # check
                current_value = values[index]
                if 'center' in current_value.lower():
                    continue
                if proj_cam not in current_value:
                    return c.name()+u": 如果投射内容属于背景，那么必须使用最远的那个相机。此检查可以跳过"

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


