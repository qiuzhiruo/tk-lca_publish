# -*- coding:utf-8 -*-

import traceback
import os
import pymel.core as pm
# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"lite材质检查"
        self.description = u"在模型减面前必须有最新一版的材质"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            file_path = pm.sceneName()
            if ".model_lite." in file_path:
                self.asset_name = os.path.basename(pm.sceneName()).split('.')[0]
                asset =  self.dialog.sg.find_one('Asset', [['code', 'is', self.asset_name]], ['sg_asset_type'])
                srf_task =  self.dialog.sg.find('Task', [['entity', 'is', asset], ['content', 'is', 'surfacing']],['sg_last_version'])
                srf_latest_version = srf_task[0].get('sg_last_version')
                if srf_latest_version:
                    return ""
                else:
                    return u"lite模型减面前需要最起码有一版材质"
            else:
                return ""

        except:
            return traceback.format_exc()
    def run_fix(self):
        '''Auto Fix'''

        try:
            pass
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


