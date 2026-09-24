# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check asset model group hierarchy
#
############################################

import traceback

import os
import re
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产的 hair pass。"
        self.description = u"模型会为CFX资产制作提供毛发造型参考物，这些参考物会放在 shape 下按照资产hair_pass命名的组内。\n默认的毛发放在hair_grp组内。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        try:
            import pymel.core as pm
            asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]],
                                            ['sg_hair_pass'])
            hair_pass_list = [t['name'] for t in asset['sg_hair_pass']]
            
            lost_list=[]
            for hair_pass in hair_pass_list:
                if not pm.objExists('|master|shape|%s_grp'%hair_pass):
                    
                    lost_list.append(hair_pass+'_grp')

            over_list = []
            name_error_list=[]
            if pm.objExists('|master|shape'):
                for hair_grp in pm.listRelatives('|master|shape'):
                    if hair_grp.name() in ['hair_grp','hair_geo']:
                        continue
                    
                    if hair_grp.hasAttr('lca_hair_pass'):
                        pass_name=hair_grp.getAttr('lca_hair_pass')
                        if pass_name in lost_list:
                            lost_list.remove(pass_name)
                            continue
                        if pass_name == 'hair_grp':
                            continue
                            
                    if 'hair' in hair_grp.name():
                        if hair_grp.name().endswith('hair_grp'):
                            if hair_grp.name()[:-4] not in hair_pass_list:
                                over_list.append(hair_grp.name())
                        else:
                            name_error_list.append(hair_grp.name())
                            

                        
            # if len(lost_list)>0:
            #     return u'资产shotgun上的hair_pass在shape下未找到:'+u','.join(lost_list)
            
            # if len(over_list) > 0:
            #     return u'这些hair_grp在资产的shotgun里的hair_pass下未找到:' + u','.join(over_list)
            
            if len(name_error_list)>0:
                return u'这些带hair的grp命名没有以hair_grp结尾:'+u','.join(name_error_list)

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


