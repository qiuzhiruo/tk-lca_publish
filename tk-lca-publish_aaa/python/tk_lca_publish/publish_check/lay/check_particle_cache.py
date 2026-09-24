# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import traceback

import os
import re
import pymel.core as pm

import sys

# sys.path.append('/mnt/utility/toolset/lib/production/pipeline')
# sys.path.append('U:/toolset/lib/production/pipeline')


# All system check classes will use StdCheck as the class name.
class StdCheck():
    """
        dependency: check_hierarchy
    """
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查particle是否已经cache"
        self.description = u"防止动画阶段由于反复拖帧等操作，生成过多粒子，返回初始帧时maya崩溃的问题"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            pars = pm.ls(type='particle')
            if not pars:
                # there is no particle
                return ""
            # then we find that if the cache exists
            dyn = pm.ls(type='dynGlobals')
            if not dyn:
                return u"particle没有cache"
                
            for d in dyn:
                try:
                    if not d.attr('useParticleDiskCache').get():
                        return u"particle没有cache"
                except:
                    return traceback.format_exc()

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        workspace = pm.workspace(query=True, fn=True)
        if (not workspace.startswith('/mnt/work/') and not workspace.startswith('W:/')) or self.dialog.entity['name'] not in workspace:
            print 'Workspace不是正确的路径，请确保从shotgun上启动的maya，再重新尝试'
            return
        #for p in pm.ls(type='particle'):
        #    pm.particle(p, edit=True, cache=True)
        start_time = pm.playbackOptions(query=True, min=True)
        end_time = pm.playbackOptions(query=True, max=True)
        pm.dynExport(path=os.path.basename(pm.sceneName())[:-3], f='cache', mnf=start_time, mxf=end_time, oup=0, all=1)
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



