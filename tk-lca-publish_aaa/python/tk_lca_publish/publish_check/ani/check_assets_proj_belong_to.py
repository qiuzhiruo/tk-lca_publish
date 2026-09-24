# -*- coding:utf-8 -*-

import traceback

import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产是否属于当前项目"
        self.description = u"资产路径必须来自当前项目"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        self.to_fix = {}
        return

    def run_check(self):
        shot_name = self.dialog.entity['name']
        
        self.to_fix = {}
        try:
            ref_files = pm.listReferences(recursive=True)
            illegal_ref = []

            for r in ref_files:
                if not r.isLoaded():
                    continue
                path = str(r.path).replace('\\', '/')
                if 'cam.camera' in path:
                    continue
                if '/asset/' not in path:
                    continue

                ns = r.fullNamespace
                master = ns.strip(':') + ':master'
                asset_index = path.split("/").index("asset")
                proj = path.split("/")[asset_index - 1]
                if not self.dialog.project['name'].lower() == proj:
                    illegal_ref.append(master)

            if illegal_ref:
                return u"以下资产的不属于当前项目, 请禁用掉或者通知上游将资产复用到当前项目: \n" + '\n'.join(illegal_ref)

            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
