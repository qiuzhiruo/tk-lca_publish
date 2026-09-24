# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import traceback

import os
import re
import pymel.core as pm

import sys


# All system check classes will use StdCheck as the class name.
class StdCheck():
    """
        dependency: check_hierarchy
    """
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"final layout不可以使用layout rig资产"
        self.description = u"final layout不可以使用layout rig资产, 测试版本不做检查"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def find_layout_rigging(self):
        refs = pm.listReferences()
        lay_rigs = []
        for r in refs:
            if not r.isLoaded():
                continue
            if 'rig.layout_rigging' in str(r.path):
                lay_rigs.append(r)
        return lay_rigs

    def run_check(self):
        try:
            if self.dialog.version_tag == u'测试':
                print 'This is a test version of flo publish, ignore checking of layout rigging.'
                return ""
            else:
                print 'This is not a test version of flo publish, need to check layout rigging.'

            layout_rigs = self.find_layout_rigging()
            if layout_rigs:
                return u"以下资产使用了layout rigging，请替换:\n" + '\n'.join( [r.fullNamespace for r in layout_rigs] )

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        if self.dialog.version_tag == u'测试':
            print 'This is a test version of flo publish, ignore checking of layout rigging.'
            return ""
        else:
            print 'This is not a test version of flo publish, need to check layout rigging.'

        layout_rigs = self.find_layout_rigging()
        if not layout_rigs:
            return
        for r in layout_rigs:
            path = str(r.path).replace('rig.layout_rigging', 'rig.rigging')
            if os.name == 'posix':
                path.replace('Z:', '/mnt/proj')
            else:
                path.replace('/mnt/proj', 'Z:')
            if os.path.isfile( path ):
                r.replaceWith( path )
            else:
                print 'Failed to find rig.rigging version for ' + r.fullNamespace
        return

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



