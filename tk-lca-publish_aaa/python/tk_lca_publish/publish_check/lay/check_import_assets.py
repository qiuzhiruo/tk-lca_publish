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
import pymel.core as pm

MAX_GEO_FACES = 10000


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"资产不可以是import进场景,且lay组下各种示意面数不能过高"
        self.description = u"|assets 组下, 除了lay组下之外，其他组下的资产不可以是import进场景, lay组下的单几何体面数不能超过{}".format(MAX_GEO_FACES)
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            assets_children = [child for child in pm.listRelatives('|assets') if 'lay' not in str(child)]
            error_nodes = []
            too_much_faces_geo = []
            for assets_child in assets_children:
                children = pm.listRelatives(assets_child, children = True, fullPath = True)
                for child in children:
                    if str(child.nodeType()) != 'assemblyReference' and not child.isReferenced():
                        parent = pm.listRelatives(child, parent=True)[0]
                        error_nodes.append(str(parent) + '|' + str(child))

            if 'LCA_SKIP_LAY_CHECK_FACE' not in os.environ:  # for testing some days, later to remove this
                if self.dialog.step['name'] == 'lay':
                    for i in pm.listRelatives('|assets|lay', ad=True):
                        if '|ars|' in i.fullPath():
                            continue
                        if i.nodeType() == 'mesh' and not i.name().endswith('Orig') and i.numFaces() > MAX_GEO_FACES:
                            too_much_faces_geo.append(i.parent(0).name())

            err_msg = ''
            if error_nodes:
                err_msg += u'[必须是Ref]以下节点不为Reference或AR:\n%s\n已经帮您选中了，请在大纲中按F查看' % (
                    '\n'.join(error_nodes))
                pm.select(error_nodes)
            if too_much_faces_geo:
                err_msg += u'以下几何体面数超过了{}, 请减少面数:\n{}'.format(MAX_GEO_FACES,
                                                              '\n'.join(
                                                                  too_much_faces_geo))

            return err_msg

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
