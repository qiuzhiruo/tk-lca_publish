# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Zhang Shirui
#
# Date: 2015.06
#
# Description: 
#
############################################

import os
import traceback
from proc.function_running_time import record_time

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"hair_patch转换。"
        self.description = u"将hair_patch多边形面片转换为NURBS。"
        return

    @record_time(__file__)
    def proceed(self):
        try:
            import maya.cmds as cmds
            if cmds.objExists('|master|shape|hair_patch_grp'):
                nurbs_grp = cmds.duplicate('|master|shape|hair_patch_grp', rr=True, n='nurbs_hair_grp' )
                l_shapes = cmds.ls(nurbs_grp,lf=True, l=True, dag=True)
                l_g_grp = []
                for s in l_shapes:
                    if s.endswith('trimmer_meshShape'):
                        continue
                    obj = cmds.listRelatives(s, p=True, f=True)[0]
                    subd = cmds.polyToSubdiv(s, ch=False, ap=False, aut=True)[0]
                    cmds.delete(s)
                    nurbs = cmds.subdToNurbs(subd, ch=False, aut=True)[0]
                    cmds.delete(subd)
                    cmds.ungroup(nurbs)
                    cmds.ungroup(obj)
                    nurbs = str(nurbs) + '_1'
                    nurbs = cmds.rename(nurbs, 'nurbs_' + str(obj).split('|')[-1])
                    nurbs_shape = cmds.listRelatives(nurbs, c=True)[0]
                    nurbs_shape = cmds.rename(nurbs_shape, nurbs + 'Shape')
                    len_v = cmds.arclen(nurbs + '.u[0.0]')
                    len_u_0 = cmds.arclen(nurbs + '.v[0.0]')
                    len_u_1 = cmds.arclen(nurbs + '.v[1.0]')
                    if max(len_v, len_u_0, len_u_1) != len_v:
                        cmds.reverseSurface(nurbs, d=3, ch=False, rpo=True)
                        len_u_0 = cmds.arclen(nurbs + '.v[0.0]')
                        len_u_1 = cmds.arclen(nurbs + '.v[1.0]')
                    if not len_u_0 > len_u_1:
                        cmds.reverseSurface(nurbs, d=1, ch=False, rpo=True)

                l_grp = cmds.listRelatives(nurbs_grp, typ='transform', ad=True, f=True)
                for m in l_grp:
                    if len(cmds.listRelatives(m, ad=True))>1:
                        l_g_grp.append(m)
                for g in l_g_grp:
                    cmds.rename(g, 'nurbs_' + str(g).split('|')[-1])
                if cmds.objExists('|master|shape|nurbs_hair_grp|trimmer_mesh'):
                    cmds.delete('|master|shape|nurbs_hair_grp|trimmer_mesh')
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
