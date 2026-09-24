# -*- coding:utf-8 -*-
__author__ = 'huangxin'

import logging
import os
import sys
import traceback
import production.pipeline.utils as pplu
from production.farm_ip import LcaFarmIPManage

FARMTEMPLATE_ID=LcaFarmIPManage().MASTERCACHE

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录模型mesh信息。"
        self.description = u"将模型的mesh层级结构，名称，点线面数记录为下游组比对做准备。"
    
    def proceed(self):
        try:
            if self.dialog.task['name'] != 'cloth':
                return ''

            import production.python_job as ppj
            import render.muster_functions.muster_user_data_utils as mudu
            

            tokens = os.path.dirname(__file__).replace('\\', '/').split('/')
            mesh_xml_py = '/'.join(tokens[:-2]) + '/proc/mesh_xml_cmd.py'

            filename = os.path.join(self.dialog.version_dir, os.path.basename(self.dialog.version_dir) + '.ma').replace('\\', '/')
            cache_dir = os.path.join(self.dialog.version_dir, 'cache').replace('\\', '/')

            try:
                username = mudu.getUserFullFromDB(self.dialog.user_name)
                user = username['full_name']
            except:
                user = 'farmer'
            
            job_list = []

            for chara in os.listdir(cache_dir):
                mesh_xml = os.path.join(cache_dir, chara, 'geo') + '/mesh.xml'
                abc_file = os.path.join(cache_dir, chara, 'geo') + '/geo_hi.abc'
                if os.path.isfile(mesh_xml):
                    os.remove(mesh_xml)

                cmd = mesh_xml_py + ' -a ' + abc_file + ' -m ' + mesh_xml
                job_id = ppj.send_job('',
                    args=cmd,
                    proj=self.dialog.project['name'].upper(),
                    job_name_prefix='[Mesh Xml]'+os.path.basename(filename)+'_'+chara+'_meshxml by '+user,
                    step='CFX',
                    user=self.dialog.user_name,
                    url=FARMTEMPLATE_ID,
                    submitdl=True,
                    python_exe=pplu.get_dcc_launcher(proj=self.dialog.project['name'].lower(),dcc='mayapy')
                )
                if job_id == -1:
                    print 'Farm submit mesh xml error: ', chara
                else:
                    job_list.append(job_id)

            print "Export mesh xml job:", job_list
            
        except:
            return traceback.format_exc()
        return ''

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
