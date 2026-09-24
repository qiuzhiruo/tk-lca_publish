# -*- coding: UTF-8 -*-
# @Time:2023/3/7 下午4:19
# @Author:yulu
import os
import traceback
import pymel.core as pm
import maya.mel as mel

import production.mayautils as mutils
from production.translate_os_path import osPathConvert


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产扩展名"
        self.description = u"资产rig.rigging不可以是以ma结尾,需要替换成mb 。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def get_riggings(self):
        error_rigging = {}
        l_masters = pm.ls('master', recursive=True, referencedNodes=True)
        for master in mutils.progressIter(l_masters,
                                          status=self.get_check_name(),
                                          isInterruptable=False):
            node = pm.referenceQuery(master, referenceNode=True, topReference=True)
            ma_path = pm.referenceQuery(node, filename=True, un=True, wcn=True)
            tokens = ma_path.split('/')
            if 'asset' not in tokens:
                continue

            i = tokens.index('asset')
            version_name = tokens[i + 5]
            if 'rig.' in version_name:
                if ma_path.endswith('ma'):
                    mb_path = ma_path.replace('.ma', '.mb')
                    error_rigging[node] = mb_path
        return error_rigging

    def run_check(self):
        try:
            error_assets_rigging = self.get_riggings().keys()
            if len(error_assets_rigging) > 0:
                return u'这些资产rig.riging使用的路径是以ma结尾: ' + u' '.join(error_assets_rigging)
            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            no_mb_nodes = []
            error_assets_rigging = self.get_riggings()
            for node_name, rig_file in error_assets_rigging.iteritems():
                if os.path.isfile(osPathConvert(rig_file)):
                    ref_node = pm.FileReference(node_name)
                    ref_rn = ref_node.refNode
                    mel.eval('file -loadReferenceDepth "asPrefs" -loadReference "%s" "%s";' % (
                        ref_rn, osPathConvert(rig_file)))
                else:
                    no_mb_nodes.append(node_name)
            if no_mb_nodes:
                return u'这些资产 {} 没有mb文件' + u' '.join(no_mb_nodes)
            else:
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
