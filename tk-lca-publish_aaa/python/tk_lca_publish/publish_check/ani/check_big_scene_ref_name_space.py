# -*- coding:utf-8 -*-


import traceback
import os
import pymel.core as pm
import re
import json
import ani.lca_cleanup_file.functions as utils



# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查大场面命名空间是否添加镜头号且规范。"
        self.description = u"如果d90630的拆分文件d90685，horse_soldier其名称空间应该是horse_soldier685或者horse_soldier6851"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def get_current_shot_info(self):
        proj_name = self.dialog.project['name']
        seq_name = self.dialog.entity['name']
        shot_name = self.dialog.entity['name']

        return proj_name, seq_name, shot_name

    def check_current_shot_big(self):
        big_scenes = False
        proj, seq, shot = self.get_current_shot_info()
        # print proj
        # print seq
        # print shot

        current_shot_sg_info = self.dialog.sg.find_one("Shot", [["project.Project.name", "is", proj], ["code", "is", shot]],
                                           ["sg_sequence", "description", "code"])
        # print current_shot_sg_info
        current_shot_description = current_shot_sg_info["description"]
        current_shot_description_str = json.dumps(current_shot_description, ensure_ascii=False, indent=4).decode(
            'utf-8')
        # print current_shot_description_str

        if u"大场面拆分镜头" in current_shot_description_str:
            big_scenes = True
        return big_scenes

    def run_check(self):
        strs = u''
        try:
            if self.check_current_shot_big():
                print 1
                get_wrong_dict = self.findWrongNameSpace()
                print 2, get_wrong_dict
                if len(get_wrong_dict.keys()):
                    for item in get_wrong_dict.items():
                        strs += u'目前是%s--->应该为%s\n' % (item[0], item[1])

                    return u'以下名称空间不规范\n' + strs
                else:
                    return ''
            else:
                print u'不是大场面拆分镜头不检查'
                return ''

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            # input_dict = self.findWrongNameSpace()
            # self.replaceRefNamespace(input_dict)
            utils.fixBigSceneNamespaces()
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

    def findWrongNameSpace(self):
        no_match_dict = {}
        for ref in pm.system.getReferences().items():
            currentNameSpace = ref[0]
            ref_file = str(ref[1])
            if '/assets/' in ref_file:
                right_name = os.path.splitext(os.path.basename(ref_file))[0]
                shot_name = self.dialog.entity['name'][3:]
                if currentNameSpace == '%s%s' % (right_name, shot_name):
                    continue

                if currentNameSpace.startswith('%s%s' % (right_name, shot_name)) and currentNameSpace[len(right_name):].isdigit():
                    continue
                # loose case, trailing digits is ok
                else:
                    right_name_space = os.path.splitext(os.path.basename(ref_file))[0] + self.dialog.entity['name'][3:]
                    no_match_dict[currentNameSpace] = right_name_space

        return no_match_dict

    def replaceRefNamespace(self, input_dict):
        if len(input_dict.keys()) > 0:
            for item in input_dict.items():
                old_name_space = item[0]
                new_name_space = item[1]
                try:
                    pm.system.namespace(ren=(old_name_space, new_name_space))
                except:
                    print u'namespace 需要手动修复'

        pm.system.saveFile(f=1)

