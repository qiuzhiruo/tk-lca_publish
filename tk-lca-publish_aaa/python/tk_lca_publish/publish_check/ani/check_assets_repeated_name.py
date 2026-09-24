# -*- coding:utf-8 -*-

__author__ = 'xiangquan'

import traceback
import os
import pymel.core as pm
import re
# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查单个资产下，去掉namespace后是否有节点重名"
        self.description = u"为了保证cacheman能顺利出cache，一个资产下的所有节点都不能重名"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            from cfx.lcaCfxCache import functions as func 
            
            grps = pm.listRelatives('assets', children = True)
            if 'lay' in grps:
                grps.remove('lay')
            
            conflict_list = []
            for grp in grps:
                children = pm.listRelatives(grp, children = True)
                for child in children:
                    grp_conflict = func.detectConflict(child)
                    if grp_conflict:
                        conflict_list.append(str(grp_conflict))
            
            if conflict_list:
                msg = '\n'.join(conflict_list)
                return 'Name Conflict:\n' + msg
            else:
                return ''
        
        except:
            return traceback.format_exc()
        
    def run_fix(self):
        '''Auto Fix'''

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

    def findWrongNameSpace(self):
        no_match_dict={}
        for ref in pm.system.getReferences().items():
            currentNameSpace=ref[0]
            ref_file=str(ref[1])
            if '{' in os.path.basename(ref_file):
                num=re.findall("{(\d+)}",ref_file)[0]
                right_name_space=os.path.splitext(os.path.basename(ref_file))[0]+num
            else:
                right_name_space=os.path.splitext(os.path.basename(ref_file))[0]
            if not right_name_space in currentNameSpace :
                    if re.findall("(\D+)",currentNameSpace)[0]!=re.findall("(\D+)",right_name_space)[0]:
                        no_match_dict[currentNameSpace]=right_name_space    
        return no_match_dict
    
    def replaceRefNamespace(self,input_dict):
        if len(input_dict.keys())>0:
            for item in input_dict.items():
                old_name_space=item[0]
                new_name_space=item[1]
                try:
                    pm.system.namespace(ren=(old_name_space,new_name_space))

                except:
                    print u'namespace 需要手动修复'
        pm.system.saveFile(f=1)