# -*- coding: utf-8 -*-

"""
    @Date: 7/9/2511:38 AM
    Descriptions:
    
"""
__author__ = 'huangsheng'

import os
import sys
import cfx.feather_curves_loft.export_feather_data as efd
import cfx.feather_curves_loft.submit_farm as submit_farm
reload(submit_farm)
import production.pipeline.permission_control as ppc
import time

class StdProcess(object):

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出 Feather Curves data，供srf画贴图使用"
        self.description = u"导出 .mel,.abc, .json 等文件"

    def proceed(self):
        if os.path.isdir(self.dialog.version_dir):
            feather_dir = os.path.join(self.dialog.version_dir, "feather_info")
            if not os.path.exists(feather_dir):
                os.makedirs(feather_dir)
            pc = ppc.PermissionControl(os.path.dirname(feather_dir))
            pc.change_mod_permission(777)
            # export .mel .abc
            efd.main(feather_dir)
            time.sleep(1)
            efd.main(feather_dir)
            # loft curves
            proj = self.dialog.project['name']
            asset = self.dialog.entity['name']
            submit_farm.submit(proj,asset, feather_dir)
            return ""
        else:
            return 'The publish version not exists: '+self.dialog.version_dir

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description




if __name__ == '__main__':
    print("")