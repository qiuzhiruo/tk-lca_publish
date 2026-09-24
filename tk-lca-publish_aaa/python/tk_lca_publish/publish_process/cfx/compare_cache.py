# -*- coding:utf-8 -*-
__author__ = 'huangxin'

import logging
import os
import sys
import traceback
import production.pipeline.lcProdProj as lcpp

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"对比最新版动画缓存"
        self.description = u"将本次publish的缓存和最新版动画缓存的bodygeo作对比，有差别则发note"
    
    def proceed(self):
        try:
            if self.dialog.task['name'] != 'cloth':
                return ''

            import cfx.cfx_cache_check.compare_cfx_cache as check_cfx

            cache_dir = os.path.join(self.dialog.version_dir, 'cache').replace('\\', '/')
            job_list = []

            ppinfo = lcpp.lcProdProj()
            ppinfo.setProj(self.dialog.project['name'].lower())
            for chara in os.listdir(cache_dir):
                if ppinfo.getAssetType(chara) != 'chr':
                    continue
                abc_file = os.path.join(cache_dir, chara, 'geo') + '/geo_hi.abc'
                print self.dialog.project['name'], abc_file
                job_id = check_cfx.send_cache_job(self.dialog.project['name'].lower(), abc_file)
                if job_id == -1:
                    print 'Farm submit diff cache error: ', chara
                else:
                    job_list.append(job_id)

            print "Submit Diff Cfx Ani job:", job_list
            
        except:
            return traceback.format_exc()+'\n'+self.dialog.project['name']+'\n'+abc_file
        return ''

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
