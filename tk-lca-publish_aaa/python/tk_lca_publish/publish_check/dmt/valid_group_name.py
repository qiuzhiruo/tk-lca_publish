# -*- coding:utf-8 -*-

import traceback

import os
import shutil
import nuke

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查Stereo_Projection内的组名称必须以DMT_3D_Proj开头"
        self.description = u"Stereo_Projection内的组名称必须以DMT_3D_Proj开头"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def deselectAll(self):
        try:
            for n in nuke.selectedNodes():
                n['selected'].setValue(False)
        except:
            pass

    def run_check(self):
        try:
            backdrop = nuke.toNode('Stereo_Projection')
            if not backdrop:
                return u"找不到 Stereo_Projection backdrop!"

            self.deselectAll()
            backdrop.selectNodes()
            sel = nuke.selectedNodes()

            # analysing read and read geo nodes
            grps = [ s for s in sel if s.Class() == 'Group' ]

            if len(grps) <= 0:
                return u"Stereo_Projection内没有发现投射组"

            illegal_grp = []
            for g in grps:
                if not 'DMT_3D_Proj' in g.name():
                    illegal_grp.append( g )

            if len(illegal_grp)>0:
                return u"发现以下组的名称不以DMT_3D_Proj开头:\n"+'\n'.join(illegal_grp)

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


