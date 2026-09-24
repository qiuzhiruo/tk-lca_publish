# -*- coding:utf-8 -*-

import pymel.core as pm
import os
from proc.function_running_time import record_time


class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出to_srf"
        self.description = u"输出给材质映射的高模， 输出后删除to_srf"
        return

    @record_time(__file__)
    def proceed(self):

        version_dir = os.path.join(self.dialog.publish_root, self.dialog.version_name)
        if pm.objExists('|master|shape|to_srf'):
            pm.select('|master|shape|to_srf')
            to_srf_dir = os.path.join(version_dir, 'to_srf')
            if not os.path.exists(to_srf_dir):
                os.mkdir(to_srf_dir)
            pm.exportSelected(os.path.join(to_srf_dir, os.path.basename(pm.sceneName())))

            if len(pm.listRelatives('|master|shape')) == 1 and 'to_srf' in pm.listRelatives('|master|shape'):
                pm.delete('|master|shape')
            else:
                pm.delete('|master|shape|to_srf')

        return ''

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
