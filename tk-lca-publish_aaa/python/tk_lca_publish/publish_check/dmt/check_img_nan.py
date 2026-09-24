# -*- coding:utf-8 -*-
import os
import sys
import nuke
import json
import traceback

sys.path.append('{}/nuke/python'.format(os.getenv('LC_APP_PATH')))
import check_dmt_img_nan as cdin


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查DMT投射是否漏边"
        self.description = u"检查DMT投射是否因为投射贴图过小或者相机变化过大导致有边缘部分漏出"
        self.auto_fix = False
        self.duty = u"艺术家本人。"

        self.start_frame = nuke.root().firstFrame()
        self.last_frame = nuke.root().lastFrame()

        return

    def run_check(self):
        try:
            file_name = nuke.root().name()
            result_json = file_name.replace('.nk', '.dmt_check.json')
            print('result_json: {}'.format(result_json))
            if os.path.exists(result_json):
                with open(result_json, 'r') as json_file:
                    json_data = json.load(json_file, encoding='utf-8')
                result = json_data['check_result']
            else:
                result = cdin.check_dmt_nodes(self.start_frame, self.last_frame)

            if result:
                return result

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
