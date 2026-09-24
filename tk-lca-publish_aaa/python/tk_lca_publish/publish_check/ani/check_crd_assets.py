# -*- coding: utf-8 -*-
import traceback
import pymel.core as pm
import maya.cmds as cmds

import production.mayautils as mutils


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否是crd资产(群集表演z1*)"
        self.description = u"目前群集场为z1*, 检测镜头中用到的资产是否为crd资产"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def get_error_crd_assets(self):
        error_crd_assets = []
        error_crd_assets_RN = []
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

            asset_type = tokens[i + 1]
            asset_name = tokens[i + 2]

            proj_name = tokens[i - 1]
            if 'prp' in tokens:
                # 先进行判定，是不是名字里带 crd # 注意，此处不用判定名称，制片默认都会加 群集道具 的 tag
                # if not (asset_type == 'crd' or '_crd' in asset_name):
                asset_tags = self.dialog.sg.find_one("Asset", [['project', 'name_is', proj_name],
                                                               ['code', 'is', asset_name]], ['tags'])
                # 再进行判定，看下 tags 里有没有 群集道具 关键字
                if asset_tags.get('tags'):
                    crd_prp = False
                    for tag in asset_tags['tags']:
                        if u'群集道具' in tag['name'].decode('utf-8'):
                            crd_prp = True
                    if not crd_prp:
                        error_crd_assets.append(master)
                        error_crd_assets_RN.append(node)
                else:
                    error_crd_assets.append(master)
                    error_crd_assets_RN.append(node)
            else:
                if not (asset_type == 'crd' or '_crd' in asset_name):
                    error_crd_assets.append(master)
                    error_crd_assets_RN.append(node)

        return error_crd_assets, error_crd_assets_RN

    def run_check(self):
        try:
            if self.dialog.step['name'] == 'ani' and self.dialog.entity['name'].startswith('z1'):
                print 'Check crd assets for ani z1*!'
                if self.dialog.project['name'].lower() == 'xun':
                    if int(self.dialog.entity['name'][-3:])<31 or 49<int(self.dialog.entity['name'][-3:])<321 or 321<int(self.dialog.entity['name'][-3:])<323 or int(self.dialog.entity['name'][-3:])>339:
                        error_crd_assets, error_crd_assets_RN = self.get_error_crd_assets()
                        if len(error_crd_assets) > 0:
                            cmds.select(error_crd_assets)
                            return u'以下选中的资产需要替换成对应的crd资产: ' + u' '.join(error_crd_assets_RN)
                    else:
                        print 'Skip z1* seq z11031 to z11049,z11323 to z11339 !'
                else:
                    error_crd_assets, error_crd_assets_RN = self.get_error_crd_assets()
                    if len(error_crd_assets) > 0:
                        cmds.select(error_crd_assets)
                        return u'以下选中的资产需要替换成对应的crd资产: ' + u' '.join(error_crd_assets_RN)
            else:
                print 'Skip not ani and not z1* seq!'

            return ''
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
