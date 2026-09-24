# -*- coding:utf-8 -*-
__author__ = 'huangxin'

import os
import sys
import traceback
import shutil
import cfx.cfx_felt_pipeline.hair_pass_utils as hpu


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出渲染cache版本"
        self.description = u"Daily版导出渲染mov记录的cache版本，Downstream版导出选择的cache版本。"
    
    def proceed(self):
        proj = self.dialog.project.get("name")
        shot = self.dialog.entity_name
        try:
            if self.dialog.publish_mode == 0:
                mov_file = self.dialog.l_preview_files[0]
                cache_status_file = mov_file[:-4]+'/cache_status.txt'
                if os.path.isfile(cache_status_file):
                    shutil.copyfile(cache_status_file, self.dialog.version_dir+'/cache_status.txt')
            else:
                n_cache_items = self.dialog.w_publish_file.listWidget_cache.count()
                if n_cache_items is 0:
                    self.dialog.print_log(u'只publish hair pass信息')
                    return ''
                cache_dir_list = list()
                for i in range(n_cache_items):
                    cache_dir = self.dialog.w_publish_file.listWidget_cache.item(i).text()
                    if not cache_dir:
                        continue
                    if cache_dir.endswith('/'):
                        cache_dir = cache_dir[:-1]
                    cache_dir_list.append(cache_dir)
                cache_list = list()
                for cd in cache_dir_list:
                    cl = [cd+'/cache/'+asset for asset in os.listdir(cd+'/cache')]
                    cache_list.extend(cl)
                if cache_list:
                    with open(self.dialog.version_dir+'/cache_status.txt', 'w') as f:
                        f.write('\n'.join(cache_list))
            
        except:
            return traceback.format_exc()
        return ''

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
