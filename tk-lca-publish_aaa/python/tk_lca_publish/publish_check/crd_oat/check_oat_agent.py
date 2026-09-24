# -*- coding: utf-8 -*-
# @Time    : 18-5-8 下午2:56
# @Author  : zhangzheng
__author__ = 'zhangzheng'
__maintainer__ = 'zhangzheng'

import traceback
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查文件内的agent是否正确"
        self.description = u"文件内有唯一的AgentGroup并在最高层"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            if len(pm.ls(type='McdAgentGroup')) != 1:
                return u'请确保文件内有唯一的AgentGroup!!!'
            agentgrp = pm.ls(type='McdAgentGroup')[0]
            if agentgrp.getParent():
                return u'请确保AgentGroup组在最高层没有其他父物体'
    
            topgrps = [i for i in pm.ls(assemblies=True) if i not in [u'persp', u'top', u'front', u'side']]
            if len(topgrps) != 1:
                topgrps.remove(agentgrp)
                topgrp_text = ','.join(topgrps)
                return u'请确保场景中最高层只有AgentGroup,\n\t没有多余的相机和其他物体\n' + topgrp_text
            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

