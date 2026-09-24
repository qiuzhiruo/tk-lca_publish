# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2017.12
#
# Description: As the description shows below
#
############################################

import os
import traceback
import glob
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 Yeti texutre 节点调用的贴图是否正确"
        self.description = u"检查 Yeti texutre 节点调用的贴图是否存在；贴图路径不带空格。"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return


    def run_check(self):
        try:
            l_errs = []
            for yeti_node in pm.ls(type = 'pgYetiMaya'):
                for tex_node in pm.pgYetiGraph(yeti_node, listNodes=1, type='texture'):
                    tex = pm.pgYetiGraph(yeti_node, node=tex_node, param='file_name', getParamValue=True)
                    if ' ' in tex:
                        l_errs.append(' '.join([u'贴图路径中有空格:', yeti_node.nodeName(), tex_node, tex]))
                        continue

                    if '<UDIM>' in tex:
                        if len(glob.glob(tex.replace('<UDIM>', '*'))) == 0:
                            l_errs.append(' '.join([u'找不到符合命名的UDIM贴图文件:', yeti_node.nodeName(), tex_node, tex]))
                    else:
                        if not os.path.isfile(tex):
                            l_errs.append(' '.join([u'找不到贴图文件:', yeti_node.nodeName(), tex_node, tex]))

            return '\n'.join(l_errs)                
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


