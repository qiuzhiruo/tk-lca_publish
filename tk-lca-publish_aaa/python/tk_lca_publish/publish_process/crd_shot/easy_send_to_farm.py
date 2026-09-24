# -*- coding: utf-8 -*-
__author__ = 'lingbo'
__maintainer__ = 'lingbo'

import sys
import os
import getpass
# sys.path.append('/mnt/utility/toolset/lib/production')
sys.path.append('/mnt/proj/software/muster8.5.7-sdk/libs/linux64/python27')
import production.python_job as ppj
from production.farm_ip import LcaFarmIPManage

#SCRIPT_PATH = '/mnt/utility/toolset/tools/crd/miarmy_cache/miarmy_do_cache.py'
SCRIPT_PATH = '{}/tools/crd/miarmy_cache/split_miarmy_cache.py'.format(os.getenv('LC_TOOLSET'))
#SCRIPT_PATH = '/mnt/public/Share/qinlingbo/git/lcatools/tools/crd/miarmy_cache/split_miarmy_cache.py'
import traceback


# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"提交publish文件到农场出cache然后提交自检"
        self.description = u"提交publish文件到农场出cache然后提交自检。"
        return
    
    def proceed(self):
        try:
            work_file = self.dialog.publish_ma
            print 'work file is ',work_file
            shot = self.dialog.sg.find_one('Shot', [['id', 'is', self.dialog.entity['id']]],
                                           ['sg_cut_in', 'sg_cut_out', 'sg_cut_duration', 'sg_ani_cut_in','sg_ani_cut_out'])

            fstart = int(shot['sg_cut_in']) - 2
            print 'fstart is ',fstart
            print 'fstart type is ',type(fstart)
            fend = int(shot['sg_cut_out']) + 2
            print 'fend is ', fend
            print 'fend type is ', type(fend)
            proj = self.dialog.project['name'].lower()
            #by_user = self.dialog.user['name']
            by_user = getpass.getuser()
            print 'by_user is ',by_user
            print 'by_user type is ',type(by_user)
            #output_floder = os.path.join(self.dialog.version_dir, 'crowd_miarmy','abc')

            output_floder = self.dialog.version_dir

            mayapy = '{}/launchers/{}/linux/mayapy'.format(os.getenv('LCA_REZ'), proj.lower())
            #splitFileSubmit(file_path,base_floder,startFrame,endtFrame,proj,by_user,step)
            args_str = work_file + ' ' + output_floder + ' '+ str(fstart) + ' ' + str(fend) + ' ' + proj + ' ' + by_user + ' 500'
            job_id = ppj.send_job(SCRIPT_PATH,
                                  proj=proj,
                                  url=LcaFarmIPManage().MASTERCACHE,
                                  args=args_str,
                                  user=by_user,
                                  priority = 200,
                                  step='CRD',
                                  python_exe=mayapy,
                                  job_name_prefix='[CrdCache]%s: '%proj.upper() + work_file)
    
            print job_id
            return ""
        
        except:
            return traceback.format_exc()
    
    def get_process_name(self):
        return self.process_name
    
    def get_description(self):
        return self.description






