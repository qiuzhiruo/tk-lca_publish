# -*- coding:utf-8 -*-
import os,sys
import getpass
import traceback
import production.python_job as ppj

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出CFX usd文件"
        self.description = u""
        return

    def proceed(self):
        scp = '{}/tools/cfx/cfxAsset_usd_submission.py'.format(os.getenv('LC_TOOLSET'))
        python_exe = '{}/launchers/gen/linux/lca_python'.format(os.getenv('LCA_REZ'))
        proj_name = self.dialog.project['name']
        ast_name = self.dialog.entity['name']
        cmd_args = proj_name + ' ' + ast_name
        job_id = ppj.send_job(scp,
                              proj=proj_name.upper(),
                              args=cmd_args,
                              python_exe=python_exe,
                              user=getpass.getuser(),
                              job_name_prefix='cfx usd'+ast_name,
                              submitdl=True)

        print('Send cfx build asset usd to farm,  ', job_id)
        return ""

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


