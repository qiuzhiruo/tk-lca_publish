# -*- coding: utf-8 -*-
# @Time    : 18-8-9 上午11:44
# @Author  : zhangzheng
__author__ = 'zhangzheng'
__maintainer__ = 'zhangzheng'

import sys
import os
# sys.path.append('/mnt/utility/toolset/lib/production')
sys.path.append('/mnt/proj/software/muster8.5.7-sdk/libs/linux64/python27')
import production.python_job as ppj
from production.farm_ip import LcaFarmIPManage

SCRIPT_PATH = '{}/tools/crd/miarmy_cache/miarmy_do_cache.py'.format(os.getenv('LC_TOOLSET'))

import traceback


# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"提交publish文件到农场出cache"
        self.description = u"提交publish文件到农场出cache。"
        return
    
    def proceed(self):
        try:
            work_file = self.dialog.publish_ma
            print 'work file is ',work_file
            shot = self.dialog.sg.find_one('Shot', [['id', 'is', self.dialog.entity['id']]],
                                           ['sg_cut_in', 'sg_cut_out', 'sg_cut_duration', 'sg_ani_cut_in',
                                            'sg_ani_cut_out'])

            fstart = shot['sg_cut_in']
            print 'fstart is ',fstart
            print 'fstart type is ',type(fstart)
            fend = shot['sg_cut_out']
            print 'fend is ', fend
            print 'fend type is ', type(fend)
            proj = self.dialog.project['name'].lower()
            by_user = self.dialog.user['name']
            print 'by_user is ',by_user
            print 'by_user type is ',type(by_user)

            mayapy = '{}/launchers/{}/linux/mayapy'.format(os.getenv('LCA_REZ'), proj.lower())

            args_str = work_file + ' ' + str(fstart) + ' ' + str(fend)+' '+by_user +' '+mayapy
            job_id = ppj.send_job(SCRIPT_PATH,
                                  proj='pws',
                                  url=LcaFarmIPManage().MASTERCACHE,
                                  args=args_str,
                                  user=by_user,
                                  priority = 200,
                                  step='CRD',
                                  msg = 'send to farm ok!!!',
                                  python_exe=mayapy,
                                  job_name_prefix='[CrdCache]PWS: ' + work_file)
    
            print job_id
            return ""
        
        except:
            return traceback.format_exc()
    
    def get_process_name(self):
        return self.process_name
    
    def get_description(self):
        return self.description






