# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: No referenced nodes under |master.
#
########################################################################################

import traceback
import pymel.core as pm
import maya.cmds as mc

def check_master_move(master='master', poly='poly', tol=0.01):
    """
    check master move

    @param master: master
    @type master : str

    @param poly : poly
    @type poly : str

    @return  [double_moved_objs, none_moved_objs]
    @retval list

    """
    mc.select(poly, hi=1)
    all_grp = mc.ls(sl=1)
    geos = []
    for sel in all_grp:
        # sel=all_grp[0]
        shapes = mc.listRelatives(sel, s=1, pa=1)
        if shapes:
            geos.append(sel)

    parent = mc.listRelatives(master, p=1)
    temp_grp = mc.group(master)
    double_moved_objs = []
    none_moved_objs = []
    bounding_box_ys = []
    orig_bounding_box_ys = []
    bounding_boxs = []
    orig_bounding_boxs = []
    for grp in geos:
        bounding_box = mc.xform(grp, q=1, ws=1, bb=1)
        bounding_boxs.append(bounding_box)
        bounding_box_y = bounding_box[4] - bounding_box[1]
        bounding_box_ys.append(bounding_box_y)
    mc.xform(temp_grp, os=1, t=[0, 100, 0])
    for grp in geos:
        orig_bounding_box = mc.xform(grp, q=1, ws=1, bb=1)
        orig_bounding_boxs.append(orig_bounding_box)
        orig_bounding_box_y = orig_bounding_box[4] - orig_bounding_box[1]
        orig_bounding_box_ys.append(orig_bounding_box_y)
    mc.xform(temp_grp, os=1, t=[0, 0, 0])

    if parent:
        mc.parent(master, parent[0])
    else:
        mc.parent(master, w=1)
    mc.delete(temp_grp)
    i = 0
    for grp in geos:
        orig_bounding_box_y = orig_bounding_box_ys[i]
        bounding_box_y = bounding_box_ys[i]
        bounding_box = bounding_boxs[i]
        orig_bounding_box = orig_bounding_boxs[i]
        if orig_bounding_box_y - bounding_box_y > 0:
            try:
                if (abs(orig_bounding_box_y - bounding_box_y)) / bounding_box_y > tol:
                    double_moved_objs.append(grp)
                    i += 1
                    continue
            except:
                continue
            try:
                if (abs(bounding_box[4] - orig_bounding_box[4]) - 100) / bounding_box_y > tol:
                    double_moved_objs.append(grp)
                    i += 1
                    continue
            except:
                continue
        else:
            if bounding_box[4] >= orig_bounding_box[4]:
                none_moved_objs.append(grp)
                i += 1
                continue
        i += 1

    return [double_moved_objs, none_moved_objs]




# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查移动maset组有双倍位移的物体"
        self.description = u"检查移动maset组有双倍位移的物体"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:

            mistake_objs = check_master_move('master', 'poly')
            double_move_objs = mistake_objs[0]
            if double_move_objs:
                message  = u"有双倍位移的物体: "+",".join(double_move_objs)
                print message
                return message
            else:
                return ""
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        pass
    #
    # if not mc.objExists("master.save_master"):
    #     save_master = pm.PyNode("master")
    #     save_master.addAttr("save_master")

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



