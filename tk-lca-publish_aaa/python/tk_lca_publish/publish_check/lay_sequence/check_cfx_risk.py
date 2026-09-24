# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import os
import traceback
import pymel.core as pm
import math

import lay.utilities.check_char_dist as ccd;reload(ccd)

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"角色安全距离检查"
        self.description = u"检查角色发生毛发抖动的风险"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            asset_trans = pm.ls('master', recursive=True, referencedNodes=True)
            shot_assets = pm.ls(regex= '*_assets', type = 'objectSet')
            risk_contents = {}
            for shot_asset in shot_assets:
                shot_name = shot_asset.split('_')[0]
                refs = pm.sets(shot_asset, query = True)
                if not refs:
                    continue
                try:
                    node = pm.nt.Shot(shot_name + '_shot')
                    pm.currentTime(node.getStartTime())
                except Exception, e:
                    print e
                    continue
                
                cam_name = shot_name + '_cam'
                if pm.objExists(cam_name):
                    for ref in refs:
                        ref_head_ctrl = ref.rsplit(':', 1)[0] + ':layoutNeck_M_fk_ctrl3'
                        if pm.objExists(ref_head_ctrl):
                            ref_pos = pm.xform(ref_head_ctrl, query = True, worldSpace = True, matrix = True)[-4:-1]
                            print ref, ref_pos
                            safe = ccd.insideSafeZone(ref_pos, pm.PyNode(cam_name))
                            if not safe:
                                if str(shot_asset) not in risk_contents:
                                    risk_contents[str(shot_asset)] = [] 
                                risk_contents[str(shot_asset)].append(str(ref))
                            else:
                                safe = ccd.dist_to_origin(ref_pos, standard = 10000)
                                if not safe:
                                    if str(shot_asset) not in risk_contents:
                                        risk_contents[str(shot_asset)] = []
                                    risk_contents[str(shot_asset)].append(str(ref))
                        else:
                            print 'no head: ', ref
            if risk_contents:
                msg = u'以下镜头里的角色有发生抖动的危险：\n%s' % str(risk_contents)
                return msg
            
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
