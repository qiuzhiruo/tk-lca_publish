# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2020.06
#
# Description: 
#
############################################

import traceback
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 Maya 文件中 普天同庆 病毒"
        self.description = u"检查场景文件中是否有带 PuTianTongQing 的script节点"
        self.auto_fix = True
        self.duty = u"TD"
        return


    def run_check(self):
        try:
            l_infected_nodes = []
            for n in pm.ls(type='script'):
                if 'PuTianTongQing' in str(n.getAttr('before')):
                    l_infected_nodes.append(n.name())

            if len(l_infected_nodes) > 0:
                return u'发现被感染的节点:\n\t' + '\n\t'.join(l_infected_nodes)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        import pymel.core as pm
        try:
            l_infected_nodes = []
            for n in pm.ls(type='script'):
                if 'PuTianTongQing' in str(n.getAttr('before')):
                    l_infected_nodes.append(n.name())

            if len(l_infected_nodes) > 0:
                pm.delete(l_infected_nodes)
                
            import os
            import glob
            pt_list = glob.glob(r'C:\Users\*\Documents\maya\scripts\userSetup.mel')
            if pt_list:
                for pt in pt_list:
                    pt_del=pt+'.del'
                    os.rename(pt,pt_del)
            
            return ''

        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


