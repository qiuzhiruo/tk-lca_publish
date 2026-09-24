# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import traceback

import os
import re
import pymel.core as pm

import sys

# sys.path.append('/mnt/utility/toolset/lib/production/pipeline')
# sys.path.append('U:/toolset/lib/production/pipeline')
import production.pipeline.mayaReferenceUtils as mru
reload(mru)


# All system check classes will use StdCheck as the class name.
class StdCheck():
    """
        dependency: check_hierarchy
    """
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查unloaded资产。"
        self.description = u"如果存在unloaded资产，提出警告。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            ref_files = pm.listReferences( recursive=True )
            illegal_ref_asb = []
            illegal_ref_root = []
            for r in ref_files:
                try:
                    if not r.isLoaded():
                        if ':' in r.fullNamespace.strip(':'):
                            illegal_ref_asb.append(r.fullNamespace.strip(':') + ':master')
                        else:
                            illegal_ref_root.append( r.fullNamespace.strip(':') + ':master' )
                except:
                    print traceback.format_exc()

            if illegal_ref_asb:
                return u"以下资产没有载入场景，予以警告，可以跳过此检查: \n" + '\n'.join( illegal_ref_asb )
            if illegal_ref_root:
                return u"以下资产没有载入场景，应予以删除: \n" + '\n'.join( illegal_ref_root )

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        ref_files = pm.listReferences()
        for r in ref_files:
            try:
                if not r.isLoaded():
                    r.remove()
            except:
                print traceback.format_exc()

        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



