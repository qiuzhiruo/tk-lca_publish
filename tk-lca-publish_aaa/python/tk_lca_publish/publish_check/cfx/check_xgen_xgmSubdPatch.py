# -*-coding:utf-8-*-

import traceback
import pymel.core as pm
try:
    import xgenm as xg
    import xgenm.xgGlobal as xgg
except:
    pass


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查xgen xgmSubdPatch"
        self.description = u"检查xgen collection 是否创建了生长面"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            import maya.cmds as cmds

            if self.dialog.d_assets_info[self.dialog.entity['name']]['task']['name'] == 'cloth':
                return ""

            if not cmds.objExists("|master|hair"):
                return u"没有找到最高层master下面的hair组。"

            palettes = pm.ls(et="xgmPalette")
            # bad_collection = []
            bad_pathe_names = []
            for palette in palettes:
                for n2 in pm.listRelatives(palette, type='xgmDescription', ad=True):
                    l_pathe_names = [t.nodeName() for t in pm.listRelatives(n2.getParent(), type='xgmSubdPatch', ad=True)]
                    if not l_pathe_names:
                        bad_pathe_names.append(n2)

            if bad_pathe_names:
                return u'{} description下没有对应的生长面'.format(bad_pathe_names)
            else:
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