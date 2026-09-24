# -*- coding:utf-8 -*-
__author__ = 'xiangquan'


import lay.utilities.assembly_operations as assembly_ops;reload(assembly_ops)

import traceback
import os
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查scn AR 和 asb AR 是否是最新版。'
        self.description = u'检查scn AR 和 asb AR 是否是最新版。'
        self.auto_fix = False
        self.duty = u'艺术家本人和模型组'
        return

    def run_check(self):
        try:
            # e.g. [(nt.AssemblyReference('kelp_forest_asb'), kelp_forest_asb.mod.model.v001)]
            ar_not_latest = assembly_ops.check_ar_loaded_version(self.dialog.sg)
            if ar_not_latest:
                msg = u'以下scn/asb ar节点不是最新版本：\n'
                msg += u'AR节点名字      |     最新版本号'
                for ar_tuple in ar_not_latest:
                    msg += str(ar_tuple[0]) + '  |  ' + ar_tuple[1] + '\n'
                msg += u'请艺术家reload scn资产，然后重新观察画面，确认没有资产的位置出错，再继续publish过程。\n'
                msg += u'若reload之后有资产位置不对，请联系mod组，检查原因。\n'

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

