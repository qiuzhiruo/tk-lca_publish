# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.11
#
# Description: As the description shows below
#
############################################

import traceback
import pymel.core as pm

def nameIsHairSystem(name):
    for pre in ['hairSystem','pfxHair','shaveHair','shaveDisplayGroup','ShaveCurveGroup','growth']:
        if pre in name:
            return True
    return False
    
# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查CFX资产内节点和组命名"
        self.description = u"在master下有hair或者cloth组。hair组内毛发节点命名为<描述>_<类别>。没有"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return


    def node_cnt(self, keyword_list):
        l_nodes = pm.listRelatives('|master', ad=True)
        result = {}
        for keyword in keyword_list:
            result[keyword] = 0
        for n in l_nodes:
            n_name = n.name().split('|')[-1]
            if n_name in keyword_list:
                result[n_name] += 1
        return result


    def run_check(self):
        try:
            task_name = self.dialog.task['name'].lower()
            if 'hair' in task_name:
                if not pm.objExists("|master|hair"):
                    return u"没有找到最高层master下面的hair组。"

                # hair_node = pm.PyNode('|master|hair')
                # for chd in hair_node.getChildren():
                #     chd_name = chd.name()
                #     if nameIsHairSystem(chd_name) and len(chd_name.split('_')) != 2:
                #         return chd_name + u'不符合hair命名规范,请参考downL_pfxHair'

                palettes = pm.ls(et='xgmPalette')
                bad_collection = []
                for palette in palettes:
                    if palette.getParent().name() != 'hair':
                        bad_collection.append(palette.name())
                if bad_collection:
                    return u'collection: %s 必须放在hair组下!' % ','.join(bad_collection)


            elif task_name.startswith('cloth'):
                if not pm.objExists("|master|cloth"):
                    return u"没有找到最高层master下面的cloth组。"

            # for node_name in ['poly','hi', 'lo', 'rig','shape']:
            r = self.node_cnt(['poly','hi', 'lo', 'rig','shape'])
            for key in r.keys():
                if r[key] > 1:
                    return u'在master组下发现重名节点:', key

            return ''
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        # hair_node = pm.PyNode('|master|hair')
        # n_rename = 0
        # for chd in hair_node.getChildren():
        #     chd_name = chd.name()
        #     token = chd_name.split('_')
        #     if len(token) is not 2:
        #         if len(token)>2:
        #             chd.rename('_'.join(token[-2:]))
        #             n_rename+=1
        #         else:
        #             print(u'Warning: '+chd_name+u'无法自动重命名.')
        # print str(n_rename)+u' 个物体被重命名。'
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


