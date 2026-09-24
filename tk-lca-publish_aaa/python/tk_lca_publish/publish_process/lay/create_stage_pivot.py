# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2017.07
#
# Description: Proceed layout publish files
#
############################################

import os
import traceback
import copy
import math
import pymel.core as pm


D_UNITS = {'m':100.0, 'dm':1000.0, 'cm':10000.0, 'mm':100000.0}
PIVOT_DIVISION_FACTOR = 2.5

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"设定场景表演区中心"
        self.description = u"设定场景表演区中心"
        return

    def get_trans(self, n):
        """
        move cameras back to origin before re-calculating stage pivot
        :param n:
        :return:
        """
        cam_grp_t = pm.xform('|cameras', q=True, translation=True, ws=True)
        t1 = pm.xform(n, q=True, translation=True, ws=True)
        t2 = n.getAttr('rpt')
        return (t1[0] - cam_grp_t[0] + t2[0], t1[1] - cam_grp_t[1] + t2[1], t1[2] - cam_grp_t[2] + t2[2])

    # average pivot positions 
    def average_pos(self, l_pos):
        x = y = z = 0.0
        for pos in l_pos:
            x += pos[0]
            y += pos[1]
            z += pos[2]

        pivot_pos = [x/len(l_pos), y/len(l_pos), z/len(l_pos)]
        print 'pivot_pos:', str(pivot_pos)

        # if assets has translation already, we should add it too
        if pm.objExists('|assets'):
            assets_crnt_pos = pm.getAttr('|assets.translate')       # e.g. dt.Vector([0.0, 0.0, 0.0])
            print '|assets.translate:', str(assets_crnt_pos)
            pivot_pos[0] -= assets_crnt_pos[0]
            pivot_pos[1] -= assets_crnt_pos[1]
            pivot_pos[2] -= assets_crnt_pos[2]

        for i, p_value in enumerate(pivot_pos):
            pivot_pos[i] = int(round(p_value/self.pivot_step)) * self.pivot_step

        return tuple(pivot_pos)

    # Calculate pivot for the current frame, averaged by asset weight in the shot camera
    # If no chr asset is viewable, the pivot for this frame is the camera localtion
    def create_pivot(self, locname = '|stage_pivot', parent = None):

        l_trans_cam = []

        for i in range(self.cut_in, self.cut_out+1):
            pm.currentTime(i)

            trans_cam = self.get_trans(self.cam)
            l_trans_cam.append(trans_cam)

        shot_pivot = self.average_pos(l_trans_cam)
        
        loc = pm.createNode('locator').getParent()
        loc.rename(locname)
        if parent is not None:
            loc.setParent(parent)                                                                           # if parent is None , loc is set to '|'
        loc.setAttr('translate', shot_pivot)
        shot_pivot_name = '%d %d %d' % shot_pivot

        sg_pivot = self.dialog.sg.find_one('CustomEntity05', [['project', 'is', self.proj], ['code', 'is', shot_pivot_name]])
        if sg_pivot is None:
            sg_pivot = self.dialog.sg.create('CustomEntity05', {'project': self.proj, 'code':shot_pivot_name})
        print 'shot_pivot_name: ', shot_pivot_name
        print 'sg_pivot', sg_pivot
        print 'self.dialog.entity[\'id\']', self.dialog.entity['id']
        self.dialog.sg.update('Shot', self.dialog.entity['id'], {'sg_stage_pivot':sg_pivot})
        return loc


    def proceed(self):
        try:
            if pm.objExists('|stage_pivot'):
                print 'Find the stage pivot in the scene. Skip.'
                return ""

            self.proj = self.dialog.sg.find_one('Project', [['id', 'is', self.dialog.project['id']]], ['sg_unit_length'])

            if self.proj['sg_unit_length'] is not None:
                self.unit = self.proj['sg_unit_length']
            else:
                self.unit = 'dm'

            if not D_UNITS.has_key(self.unit):
                return 'Invalid unit'

            #self.pivot_step = int(D_UNITS[self.unit] / 2.5)
            self.pivot_step = int(D_UNITS[self.unit] / PIVOT_DIVISION_FACTOR)
            self.cut_in = int(pm.animation.playbackOptions(q=True, minTime=True))
            self.cut_out = int(pm.animation.playbackOptions(q=True, maxTime=True))

            if not pm.objExists(self.dialog.entity['name'] + '_cam'):
                return 'Failed to find camera: ' + self.dialog.entity['name'] + '_cam'

            self.cam = pm.PyNode(self.dialog.entity['name'] + '_cam')

            if not pm.objExists('|assets'):
                return 'Failed to find the assets group'

            self.create_pivot()

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


