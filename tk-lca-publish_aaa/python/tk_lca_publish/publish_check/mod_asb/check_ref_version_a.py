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
        self.check_name = u'检查 Assembly Reference 的资产路径是否不带版本号'
        self.description = u'检查 Assembly Reference 的资产路径是否不带版本号。'
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
                i = path_tokens.index('publish')
                v_tokens = path_tokens[i+1].split('.')

                # cty has nested assembly reference, the check should only apply to the top level
                if (v_tokens[-1].startswith('v') and v_tokens[-1][1:].isdigit()) and \
                        (path_tokens[-1].startswith('city_') if v_tokens[1] == 'cty' else True):
                    illegal_ref.append(master + u": 资产应该reference不带版本号的，而不是: " + path_tokens[i+1]
                                        + u", 如果是cty步骤资产，请保证顶层文件为city_开头而且不带版本号")
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
                    continue

                i = path_tokens.index('publish')
                v_tokens = path_tokens[i+1].split('.')
                if (v_tokens[-1].startswith('v') and v_tokens[-1][1:].isdigit()) and \
                        (path_tokens[-1].startswith('city_') if v_tokens[1] == 'cty' else True):
                    path_tokens[i+1] = '.'.join(v_tokens[:-1])
                    new_path = '/'.join(path_tokens)
                    if not os.path.isfile(new_path):
                        l_fix_failed.append(u"资产" + master + u"修复失败：找不到版本 " + new_path)
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

