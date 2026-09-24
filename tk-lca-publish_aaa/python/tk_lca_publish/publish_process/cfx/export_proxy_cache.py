# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import logging
import os
import sys
import re
import shutil
import traceback

ver_cache_path = os.path.join(os.environ['LC_UTILITY'], 'lca_sgtk_apps/tk-lca-version-cache/python/tk_lca_version_cache').replace('\\', '/')
#ver_cache_path = os.path.join(os.environ['LC_WORK'], 'home/xiangquan/sgtk/tk-lca-version-cache/python/tk_lca_version_cache').replace('\\', '/')
if ver_cache_path not in sys.path:
    sys.path.insert(0, ver_cache_path)
import get_cache_info
import cache_cmd


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出proxy.abc"
        self.description = u"提交导出proxy.abc的任务到farm上"
    
    def proceed(self):
        try:
            if self.dialog.task['name'] != 'cloth':
                return ''
            
            shot = self.dialog.sg.find_one('Shot', [['id', 'is', self.dialog.entity['id']]], ['sg_cut_in', 'sg_cut_out'])
            filename = os.path.join(self.dialog.version_dir, os.path.basename(self.dialog.version_dir) + '.ma').replace('\\', '/')
            cache_job = {'proj': self.dialog.project['name'], 
                         'packet_size': 1,
                         'max_nodes': 1, 
                         'priority': 1000,
                         'depend': '',
                         'pool': 'instances',
                         'script_file': '{}/tools/ani/render_ani_set/ani_proxy_cache.py'.format(os.getenv('LC_TOOLSET')),
                         'file': str(filename),
                         'f_start': shot['sg_cut_in'], 
                         'f_end': shot['sg_cut_out']
            }
            
            proxy_jobs = []
            cache_dir = os.path.join(self.dialog.version_dir, 'cache').replace('\\', '/')
            for chara in os.listdir(cache_dir):
                cache_job['path'] = cache_dir
                cache_job['node'] = chara
                proxy_job = cache_cmd.create_proxy_cache_job(cache_job, '')
                proxy_jobs.append(proxy_job)
            print 'proxy_jobs', proxy_jobs
            if proxy_jobs:
                try:
                    proxy_errors, proxy_ids = cache_cmd.submit_proxy_cache_jobs(proxy_jobs)
                    if proxy_errors:
                        print 'proxy error:', proxy_errors
                except Exception, e:
                    msg = 'submit proxy tasks to farm error:\n' + str(e)
                    return msg
                
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

