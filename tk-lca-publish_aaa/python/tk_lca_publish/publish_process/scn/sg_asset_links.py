# -*- coding:utf-8 -*-

import os
import traceback


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在 shotgun 上链接父子资产。"
        self.description = u"在 shotgun 上链接父子资产"
        return

    def proceed(self):
        try:
            import pymel.core as pm

            l_asset_names = []
            for n in pm.ls('master', recursive=True, referencedNodes=True):
                if os.path.isfile(pm.referenceQuery(n,  filename=True, wcn=True)):
                    asset_name = os.path.basename(pm.referenceQuery(n,  filename=True, wcn=True))[:-3]
                    l_asset_names.append(asset_name)

            for n in pm.ls(type='assemblyReference'):
                if n.getAttr('definition'):
                    asset_name = os.path.basename(n.getAttr('definition'))[:-3]
                    l_asset_names.append(asset_name)

            l_asset_names = list(set(l_asset_names))
            l_sg_assets = []
            for asset_name in l_asset_names:
                asset = self.dialog.sg.find_one('Asset', [['code', 'is', asset_name], ['project', 'is', self.dialog.project]], [])
                if asset:
                    l_sg_assets.append(asset)
                else:
                    print '==> unable find asset on shotgun:', asset_name

            # update asset link
            self.dialog.sg.update('Asset', self.dialog.entity['id'], {'assets': l_sg_assets})
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description



