# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Jamboo
#
# Date: 2025.07
#
# Description: 检查群集马缰绳解算，仅检查z11、z12
#
############################################
import traceback
import maya.cmds as cmds

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查群集镜头中的 马缰绳解算效果 是否制作 。'
        self.description = u'检查群集镜头中的 马缰绳解算效果 是否制作'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return
    
    def run_check(self):
        try:
            shot_name = self.dialog.entity['name'] #type:str
            if not shot_name.startswith('z1') :
                return ''
            wrong_namespace = Reins_Check_Helper().check_horse_reins_dyn() #type:list[str]
            if not wrong_namespace:
                return ''
            message  = u'注意,以下资产没有做马缰绳的解算{}'.format(wrong_namespace)
            return message
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
class Reins_Check_Helper(object):
    def __init__(self):
        return
    def all_refs():
        allRefNodes_list = cmds.ls(rf=1)
        allRefNodes = []
        for ref in allRefNodes_list:
            try:
                is_loaded = cmds.referenceQuery(ref, isLoaded=1)
                if not is_loaded:
                    continue
            except:
                continue

            allRefNodes.append(ref)

        return allRefNodes
    
    @staticmethod
    def get_all_references_with_namespace():
        all_refs = cmds.ls(type='reference')
        user_refs = []
        for ref in all_refs:
            try:
                if not cmds.referenceQuery(ref, isLoaded=True):
                    continue
                namespace = cmds.referenceQuery(ref, namespace=True, shortName=True)
                file_path = cmds.referenceQuery(ref, filename=True)
                if 'horse' not in file_path:
                    print("Skip ! Not a horse asset: [{}]".format(namespace))
                    continue
                user_refs.append(namespace)
                print("the user_refs,",user_refs)
            except RuntimeError as e:
                print("{} id error:{}".format(ref,e))
                continue
        print("check asset list",user_refs)
        return user_refs
    
    def check_horse_reins_dyn(self):
        horse_ref_node = self.get_all_references_with_namespace() #list[str]
        False_namespace = [] #type:list[str]
        if not horse_ref_node:
            return
        for horse_ref in horse_ref_node:
            horse_visibility_ctrl = '{}:visibility_ctrl'.format(horse_ref)
            attr_name = 'lc_reins_dyn'
            ctrl_attr = '{}.{}'.format(horse_visibility_ctrl,attr_name) #type:str
            if not cmds.objExists(ctrl_attr):
                False_namespace.append(horse_ref)
        if False_namespace:
            return False_namespace
        pass
    pass
    