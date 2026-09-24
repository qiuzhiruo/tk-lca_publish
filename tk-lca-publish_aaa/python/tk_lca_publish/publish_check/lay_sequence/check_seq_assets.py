# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback

import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查文件中是否使用了错误的reference资产。"
        self.description = u"检查文件中是否使用了不在Shotgun Sequence->Assets里的reference资产。"
        self.auto_fix = False
        self.duty = u"艺术家与pc协商"
        return

    def run_check(self):
        try:
            legal_assets_entities = self.dialog.sg.find_one('Sequence', [['project', 'is', self.dialog.project],
                                                                         ['code', 'is', self.dialog.entity['name']]],
                                                            ['assets'])
            # print self.dialog.project, self.dialog.entity['name'], 'legal_assets_entities'
            # import pprint
            # print legal_assets_entities
            if not legal_assets_entities:
                return u'Shotgun Sequence Assets内容为空，请联系pc检查。'

            legal_assets = [asset['name'] for asset in legal_assets_entities['assets']]
            all_refs = pm.ls(type = 'reference')
            illegal_assets = []
            for ref_node in all_refs:
                if ref_node.name() == 'sharedReferenceNode' or '_sharedReferenceNode' in ref_node.name():
                    continue

                if ref_node.name() == '_UNKNOWN_REF_NODE_':
                    pm.delete(ref_node)
                    continue

                if ref_node.isLoaded():
                    filename = ref_node.fileName(True, True, False).replace('.ma', '').replace('.mb', '')         # e.g. 'beauty_a.ma'
                    if filename == 'camera':
                        continue

                    if filename not in legal_assets:
                        ns = ref_node.associatedNamespace(True)
                        illegal_assets.append(ns + ':master')

            if illegal_assets:
                msg = u'以下reference资产不存在于 Shotgun Sequence Assets中，请联系pc协商解决：\n'
                msg += '\n'.join(illegal_assets)
                return msg
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return ""

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
