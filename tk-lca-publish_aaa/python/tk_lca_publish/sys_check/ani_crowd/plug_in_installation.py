# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.10
#
# Description:
#
############################################
import traceback
import platform

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查所需的插件是否已安装。"
        self.description = u"目前Maya群集需要安装Miarmy Plugin。"
        self.auto_fix = False
        self.duty = u"IT部门安装软件。"
        return

    def run_check(self):
        try:
            import pymel.core as pm
            load = False
            maya_ver = pm.about(v=1)
            for plugin in pm.pluginInfo(q=1, ls=1):
                if plugin.startswith('Miarmy'):
                    load = True
            if not load:
                if maya_ver == '2017':
                    name = 'MiarmyPro'
                    if platform.platform().lower().startswith('liunx'):
                        name = 'MiarmyProForMaya2017'
                    elif platform.platform().lower().startswith('win'):
                        name = 'MiarmyProFor'
                    try:
                        pm.loadPlugin(name, quiet=True)
                    except:
                        try:
                            if platform.platform().lower().startswith('liunx'):
                                name = 'MiarmyExpressForMaya2017'
                            elif platform.platform().lower().startswith('win'):
                                name = 'MiarmyExpress'
                            pm.loadPlugin(name, quiet=True)
                        except:
                            return u"Miarmy 未安装。"
                else:
                    name = 'MiarmyExpressForMaya%s' % maya_ver
                    try:
                        pm.loadPlugin(name, quiet=True)
                    except:
                        return u"%s未安装。" % name
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return ""

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
