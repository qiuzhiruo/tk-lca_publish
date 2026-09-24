# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Guan ZeJie
#
# Date: 2023.11
#
# Description: Check pass
#
############################################

import os
import sys
import traceback
from Katana import NodegraphAPI, Nodes3DAPI, FarmAPI


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查材质文件的pass和shotgun上的pass是否一致。"
        self.description = u"检查材质文件的pass和shotgun上的pass是否一致。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def __get_asset_pass_from_sg(self, proj, asset):
        env = os.environ.get('LCTOOLSET')
        sys.path.append(os.path.join(env, 'applications/katana_v2/Scripts'))
        import production.pipeline.ShotGunProj as csg
        asp = csg.ShotGunProj(proj)
        return [n['name'] for n in asp.get_asset_look_pass(asset)]

    def run_check(self):
        try:
            Katana_file_path = FarmAPI.GetKatanaFileName()
            tokens = Katana_file_path.split('/')
            proj = tokens[4]
            asset = tokens[7]

            lookFileNode_list = NodegraphAPI.GetAllNodesByType('LookFileBake')
            if not lookFileNode_list:
                return

            lookFileNode = lookFileNode_list[0]
            in_ports = lookFileNode.getInputPorts()
            linkedPass = []
            for i in range(2, len(in_ports)):
                old_name = in_ports[i].getName()
                if old_name.lower() != old_name:
                    Nodes3DAPI.LookFileBake.LookFileBake.RenamePassInput(lookFileNode, i, old_name.lower())
                    print 'Modify node %s pass name %s to lower %s' % (
                    lookFileNode.getName(), old_name, old_name.lower())
                linkedPass.append(old_name.lower())

            if proj and asset:
                sg_pass_list = self.__get_asset_pass_from_sg(proj, asset)

                error_pass = []
                for p in linkedPass:
                    if p not in sg_pass_list:
                        error_pass.append(p)

                if 'wet' not in sg_pass_list:
                    if 'wet' in error_pass: error_pass.remove('wet')
                    if 'wet' in linkedPass: linkedPass.remove('wet')

                if error_pass:
                    return u'Shotgun pass 和 katana文件pass不匹配。'

                elif sorted(linkedPass) != sorted(sg_pass_list):
                    return u'Shotgun pass 和 katana文件pass不匹配。'

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
