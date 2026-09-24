# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import traceback

import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产模型是否有低模版本"
        self.description = u"资产模型必须同时有低模版本，才可以被asb资产引用。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            ref = pm.ls('*:master', rn=True)
            lo = []
            for r in ref:
                try:
                    try:
                        ref_mod_file = str( pm.referenceQuery(r, f=True, wcn=True) ).replace('\\', '/')
                        if '/asb/' in ref_mod_file or '/rig/' in ref_mod_file or os.path.dirname(ref_mod_file).endswith('/res_lo'):
                            continue
                    except:
                        print 'Failed to get filename for reference: '+r.name()
                        continue
                    if not os.path.isfile( os.path.dirname(ref_mod_file) + '/res_lo/' + os.path.basename(ref_mod_file) ):
                        lo.append( r.name() )
                except:
                    pass

            if len(lo)>0:
                return u"下列资产没有低模版本，必须补上才可以被asb资产引用:" + '\n'.join(lo)

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


