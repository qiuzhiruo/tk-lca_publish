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
        self.check_name = u'检查 Assembly Reference 的是否是标准版本'
        self.description = u'Assembly Reference 的资产版本应该是 mod.model, rig.rigging, 而不应该使用一些 layout 版本。'
        self.auto_fix = True
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:
            illegal_ref = []

            for n in pm.ls(type='assemblyReference'):
                path = str(n.getAttr("definition")).replace('\\', '/')
                master = u"" + n.name()

                path_tokens = path.split('/')
                if not 'publish' in path_tokens:
                    illegal_ref.append(master + u": 版本reference不是正式publish版本 " + path)
                    continue
                i = path_tokens.index('publish')
                v_tokens = path_tokens[i+1].split('.')

                if not v_tokens[1] + '.' + v_tokens[2] in ['mod.model', 'rig.rigging'] and v_tokens[1] != 'cty':
                    illegal_ref.append(master + u": 版本必须是 cty, mod.model 或者 rig.rigging, 当前版本是 " + path_tokens[i+1])
                    continue

            if illegal_ref:
                return u"以下资产的路径非法:\n" + '\n'.join(illegal_ref)

            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            l_fix_failed = []
            for n in pm.ls(type='assemblyReference'):
                path = str(n.getAttr("definition")).replace('\\', '/')
                master = u"" + n.name()

                path_tokens = path.split('/')
                if not 'publish' in path_tokens:
                    l_fix_failed.append(u"资产" + master + u"修复失败：无法自动修复非正式publish的文件" + path)
                    continue

                i = path_tokens.index('publish')
                v_tokens = path_tokens[i+1].split('.')
                if not v_tokens[1] + '.' + v_tokens[2] in ['mod.model', 'rig.rigging'] and v_tokens[1] != 'cty':
                    if v_tokens[1] == 'mod':
                        path_tokens[i+1] = v_tokens[0] + '.' + 'mod.model'
                    elif v_tokens[1] == 'rig':
                        path_tokens[i+1] = v_tokens[0] + '.' + 'rig.rigging'
                    else:
                        l_fix_failed.append(u"资产" + master + u"修复失败：用的不是mod, cty 或者 rig 版本" + path_tokens[i+1])
                        continue

                    new_path = '/'.join(path_tokens)
                    if not os.path.isfile(new_path):
                        l_fix_failed.append(u"资产" + master + u"修复失败：找不到版本" + new_path)
                        continue
                    try:
                        n.setAttr("definition", new_path)
                    except:
                        l_fix_failed.append(u"资产" + master + u"修复失败：替换不成功 " + new_path)

            return '\n'.join(l_fix_failed)
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

