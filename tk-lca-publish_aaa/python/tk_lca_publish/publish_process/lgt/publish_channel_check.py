# -*- coding:utf-8 -*-
# import sys
# sys.path.append("/home/haojia/Work/SoftWare/pycharm-2022.1.3/debug-eggs/pydevd-pycharm.egg_FILES/")
# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=1234, stdoutToServer=True, stderrToServer=True)
# reload(sys)
# coding:utf-8
# @Author: tanghaojia
# @Date:
# @Last Modified by:   tanghaojia
# @Last Modified time:  2022-06-20
# @Last Commit:
# @Function:农场处理生成channel check mov和刷新1984


import traceback
import getpass
import os
import sys
# reload(sys)
sys.setdefaultencoding('utf-8')
# sys.path.append('/mnt/utility/toolset/lib/production')

import production.python_job as python_job
from production.farm_ip import LcaFarmIPManage


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"生成channel check mov"
        self.description = u"生成channel check mov,只有R1 DownStream才会执行这一步"
        self.proj = str(self.dialog.project['name']).lower()
        self.shot=self.dialog.entity['name']
        return


    def proceed(self):

        try:
            if 'R1' in self.dialog.version_tag:
                print self.dialog.version_tag
                nuke_python = '{}/launchers/{}/linux/nuke12.1v1'.format(os.getenv('LCA_REZ'), self.proj)
                tk_lca_publish_path = os.getenv('LCA_PUBLISH_APP')
                script = " -x {}/python/tk_lca_publish/publish_process/lgt/publish_channel_check_onfarm_process.py".format(tk_lca_publish_path)

            #
                args=self.proj +" "+self.shot
                python_job.send_job(script,
                                    proj=self.proj,
                                    url=LcaFarmIPManage().MASTERCACHE,
                                    args=args,
                                    user=getpass.getuser(),
                                    # user='tanghaojia',
                                    python_exe=nuke_python,
                                    priority=25000,
                                    pools='rv',  # only this pool can acces data of ftp
                                    job_name_prefix='[LGT Channel Check {shot}]'.format(shot=self.shot),
                                    submitdl=True
                                    )

            return ""
        except:
            return traceback.format_exc()



    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
