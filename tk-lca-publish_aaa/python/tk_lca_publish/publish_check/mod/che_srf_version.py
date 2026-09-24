# -*- coding:utf-8 -*-

import os.path
import traceback
import sys
from proc.function_running_time import record_time


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查材质最新版本数据"
        self.description = u"lite 版模型需要确保有材质版本才可以 pa  skip tag: skip_srf_version"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info


    @record_time(__file__)
    def run_check(self):
        asset = self.dialog.entity['name'].lower()

        sg_info = self.get_asset_shotgun_info(asset_name=asset)

        if sg_info:
            if 'skip_srf_version' in sg_info['tag_list']:
                print("=======skip_srf_version==========")
                return ''

        proj = self.dialog.project['name'].lower()
        asset_type = self.dialog.d_assets_info[asset]['type']
        # /mnt/proj/projects/lic/asset/chr/soilder_taiwei_a/srf/publish/soilder_taiwei_a.srf.surfacing
        if sys.platform.startswith('win'):
            srf_path = 'Z:/projects/{0}/asset/{1}/{2}/srf/publish/{2}.srf.surfacing'.format(proj, asset_type, asset)
        else:
            srf_path = '/mnt/proj/projects/{0}/asset/{1}/{2}/srf/publish/{2}.srf.surfacing'.format(proj, asset_type, asset)

        if not os.path.exists(srf_path):
            return u'材质还没有发布版本'

        err_msg = u''
        if not os.path.exists(os.path.join(srf_path, 'tex_low')):
            err_msg += u'材质缺少tex_low\n'
        if not os.path.exists(os.path.join(srf_path, 'mat_info')):
            err_msg += u'材质缺少mat_info\n'

        if err_msg:
            return err_msg

        return ''

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


