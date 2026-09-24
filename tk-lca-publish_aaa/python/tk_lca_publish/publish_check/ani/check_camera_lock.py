# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.07
#
# Description: As the description shows below
#
############################################

import os
import traceback
import pymel.core as pm

import lay.lca_camera_lock.functions as functions_cl
reload(functions_cl)
import lay.exportCamera.exportAbcCamera as eac
reload(eac)


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查摄像机是否有必要提交。"
        self.description = u"对比最新版确认，没有修改的话需要重新锁定，不再升级摄像机版本。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            cam = '{}_cam'.format(self.dialog.entity['name'])
            cam_root_rig = '{}_rig:global_ctrl'.format(cam)

            if functions_cl.is_camera_locked():
                if not pm.objExists(cam_root_rig):
                    return u'场景中未发现对应镜头的相机rig: "{}",请联系TD'.format(cam_root_rig)
                return ''
            
            if self.dialog.project['name'].upper() == 'TAP':
                return ''

            # if animation has no version, no matter camera really changes or not, we allow the camera to be publish
            if self.dialog.step['name'] == 'ani':
                ani_vers = self.dialog.sg.find('Version', [['project', 'is', self.dialog.project],
                                                               ['code', 'contains', self.dialog.entity['name'] + '.ani.animation'],
                                                               {"filter_operator": "any",
                                                                "filters": [["sg_version_type", "is", 'Checked'],
                                                                            ["sg_version_type", "is", 'Downstream']]
                                                               }
                                                               ], ['code', 'sg_version_type'])
                if ani_vers is None:
                    print 'first cam from ani, cam can be exported'
                    return ''

            cam_grp = functions_cl.get_cameras_group()
            if self.dialog.step['name'] == 'flo' and pm.attributeQuery('notes', node = cam_grp, exists = True):
                notes = cam_grp.attr('notes').get()
                cam_anim_infos = functions_cl.record_cam_keyframes()
                if notes != cam_anim_infos:
                    print 'Find difference between current and previous raw camera'
                    return ''
                else:
                    print 'The current camera is same with previous published raw camera.'
            else:
                if eac.diffcam(self.dialog.entity['name'], self.dialog.project['name'].lower()):
                    print 'Find difference between current and previous camera'
                    return ''
                else:
                    print 'The current camera is same with previous published camera.'
            if hasattr(self.dialog,'locked_cam_trans') and hasattr(self.dialog,'unlocked_cam_trans'):
                print 'self.dialog.locked_cam_trans >',self.dialog.locked_cam_trans
                print 'self.dialog.unlocked_cam_trans >',self.dialog.unlocked_cam_trans
                if self.dialog.locked_cam_trans!=self.dialog.unlocked_cam_trans:
                    return ''
            return u'未发现当前摄像机与最新版的差别，请重新锁定摄像机。'
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        # return ''
        functions_cl.relock_camera(raw = False)
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
