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

import os
import traceback
import pymel.core as pm

import production.mayautils as mutils
from production.translate_os_path import osPathConvert


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查Layout Rigging。"
        self.description = u"如果场景中使用资产有rig.rigging但用的是rig.rigging_layout，需要换过来 。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def get_layout_riggings(self):
        d_layout_rigging = {}
        l_masters = pm.ls('master', recursive=True, referencedNodes=True)
        for master in mutils.progressIter(l_masters,
                                          status=self.get_check_name(),
                                          isInterruptable=False):
            node = pm.referenceQuery(master, referenceNode=True, topReference=True)
            ma_path = pm.referenceQuery(node, filename=True)
            tokens = ma_path.split('/')
            if not 'asset' in tokens:
                continue

            i = tokens.index('asset')
            asset_name = tokens[i+2]
            version_name = tokens[i+5]
            if 'rig.rigging_layout' in version_name:
                rig_file = '/'.join(tokens[:i+5]) + '/' + asset_name + '.rig.rigging/' + asset_name + '.mb'
                d_layout_rigging[node] = rig_file

        return d_layout_rigging


    def run_check(self):
        try:
            l_layout_rigging = self.get_layout_riggings().keys()
            if len(l_layout_rigging)>0:
                return u'有些资产在使用 layout rigging: ' + u' '.join(l_layout_rigging)

            return ''

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        try:
            d_layout_rigging = self.get_layout_riggings()
            for node_name, rig_file in d_layout_rigging.iteritems():
                if os.path.isfile(osPathConvert(rig_file)):
                    ref_node = pm.FileReference(node_name)
                    ref_node.unload()
                    ref_node.replaceWith(rig_file)
                    ref_node.load()
                else:
                    return u'该资产 {} 没有 tec_rig'.format(node_name)

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


