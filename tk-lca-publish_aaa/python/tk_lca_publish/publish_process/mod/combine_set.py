# -*- coding:utf-8 -*-

#######################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Zhang Shirui
#
# Date: 2015.07
#
# Description: Combine objects in "combine_*" sets.
#
#######################################################

import os
import traceback
import pymel.core as pm
from proc.function_running_time import record_time

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"合并combine集合下物体。"
        self.description = u"合并combine集合下物体，并放置在对应层级下。"
        return

    @record_time(__file__)
    def proceed(self):
        try:

            all_sets = pm.ls(type='objectSet')

            for i in all_sets:
                if not i.name().startswith('combine_'):
                    continue
                    
                set_objs = i.members()
                
                dist_root = set_objs[0].getParent()
                
                cmb_obj = pm.polyUnite(set_objs)[0]
                cmb_obj = pm.parent(cmb_obj, dist_root)
                pm.delete(cmb_obj, ch=True)
                pm.delete(i)
                pm.rename(cmb_obj, i.name())

            # Delete empty group
            l_trans = pm.listRelatives('|master|poly|hi', ad=True, type='transform')
            if '|master|poly|hi' in l_trans:
                l_trans.remove('|master|poly|hi')

            for trans in l_trans:
                if not pm.objExists(trans):
                    continue

                l_meshes = pm.listRelatives(trans, ad=True, type='mesh')
                if len(l_meshes) == 0:
                    pm.delete(trans)
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


