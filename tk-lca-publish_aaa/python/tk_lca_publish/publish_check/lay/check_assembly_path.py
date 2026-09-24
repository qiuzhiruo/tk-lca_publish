# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description:
#
############################################
import traceback
import os
import sys
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查 Assembly Reference 的资产路径需要符合规范'
        self.description = u'Assembly Reference 的资产路径必须从本项目的publish服务器上引用；从 assembly_definition 调用；不带版本号的版本的ma文件。'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:

            illegal_ref = []

            for n in pm.ls(type='assemblyReference'):
                # e.g. path = '/mnt/proj/projects/tpr/asset/prp/wood_board_a/rig/publish/wood_board_a.rig.rigging.v001/assembly_definition/wood_board_a.ma'
                path = str(n.getAttr("definition")).replace('\\', '/')
                master = u"" + n.name()

                if '/cty/' in path : continue

                if not path.startswith('/mnt/proj') and not path.startswith('Z:'):
                    illegal_ref.append(master + u": 路径必须以/mnt/proj或Z:开头, 当前路径 "+path)
                    continue

                proj_dir = '/projects/' +  self.dialog.project['name'].lower() + '/'
                #skip inspect (flg)
                if not proj_dir in path and 'flg/' not in proj_dir:
                    illegal_ref.append(master + u": 非当前项目("+ self.dialog.project['name'] +u") 的资产"+path)
                    continue

                if sys.platform.startswith('win'):
                    path = path.replace('/mnt/proj', 'Z:')
                else:
                    path = path.replace( 'Z:', '/mnt/proj')
                if not os.path.isfile(path):
                    illegal_ref.append(master + u": 找不到文件 "+path)
                    continue

                path_tokens = path.split('/')
                if 'task' in path_tokens or not 'asset' in path_tokens or not 'publish' in path_tokens:
                    illegal_ref.append(master + u": 路径不可以有/task/, 必须含有/asset/和/publish/, 当前路径 " + path)
                    continue

                if not 'assembly_definition' in path_tokens:
                    illegal_ref.append(master + u": 需要调用 /assembly_definition/ 里的文件, 当前路径 " + path)
                    continue

                if not path.endswith('.ma'):
                    illegal_ref.append(master + u": 需要调用 ma 文件, 当前路径 " + path)
                    continue

                v_dir = path.split('/')[-3]
                tokens = v_dir.split('.')
                if len(tokens[-1]) == 4 and tokens[-1][0] == 'v' and tokens[-1][1:].isdigit():
                    illegal_ref.append(master + u": 路径版本不可以带版本号, 当前版本为 " + v_dir)
                    continue

            if illegal_ref:
                return u"以下资产的路径非法:\n" + '\n'.join(illegal_ref)

            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:

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

