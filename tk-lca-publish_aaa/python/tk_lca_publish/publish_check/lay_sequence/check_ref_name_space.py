# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: lin zhu
#
# Date: 2014.05
#
# Description:
#
############################################

import traceback
import os
import re

import pymel.core as pm
import ani.lca_cleanup_file.functions as utils

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查reference文件和namespace名称是否统一。"
        self.description = u"如果reference文件是*/shentu_cleaning.ma，其命名空间应该是shentu_cleaning或者shentu_cleaning1"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            wrong_ns_ref = self.findWrongNameSpace()
            if wrong_ns_ref:
                return u'以下资产名称空间不一致: \n' + '\n'.join( [str(r) for r in wrong_ns_ref] )
            else:
                return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            utils.fixNamespaces()
            return ''
        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

    def getNamespace(self, node, wcn=True):
        '''
        get namespace of given node, with leading string ':'
        option: wcn=True, strip tailing number
        '''
        try:
            ns_fn = lambda x: x if x.startswith(':') else ':'+x
            ns = ns_fn( pm.referenceQuery( node, namespace=True ) )
            if wcn:
                # strip tail number
                while ns[-1].isdigit():
                    ns = ns[:-1]
            return ns
        except:
            print traceback.format_exc()
            return ''

    def getPerfectNamespace(self, node, wcn=True):
        '''
        get perfect namespace by recursive parent level, this collapses child namespace to non empty parent space
        '''
        try:
            ns_fn = lambda x: x if x.startswith(':') else ':'+x
            ns = ns_fn( pm.referenceQuery( node, namespace=True, shortName=True ) )
            parent_ref = pm.referenceQuery( node, rfn=True, parent=True )
            if parent_ref:
                ns = self.getPerfectNamespace( parent_ref ) + ns
            if wcn and not pm.referenceQuery( node, rfn=True, child=True ):
                # strip tail number only on the last child
                while ns[-1].isdigit():
                    ns = ns[:-1]
            return ns
        except:
            print traceback.format_exc()
            return ''

    def findWrongNameSpace(self):
        '''
        find all assets whose namespace is not same with its reference filename
        '''
        refs = pm.ls(rf=True)
        fake_ns = []
        for r in refs:
            try:
                if not r.referenceFile():
                    print 'Can not find the associated file for reference node: ' + str(r)
                    continue

                file_ref = pm.FileReference(r)
                if not file_ref.isLoaded():
                    continue

                if file_ref.path.endswith('camera.ma'):
                    continue

                ns_src = self.getNamespace(file_ref).strip(':')
                if pm.referenceQuery(file_ref, rfn=True, parent=True):
                    perfect_ns = self.getPerfectNamespace(file_ref).strip(':')
                    if perfect_ns != ns_src:
                        fake_ns.append(file_ref.refNode)
                        print u"命名空间携带空的父级命名空间，应该手动修正: " + str(file_ref.refNode)
                        continue

                    ns_src = ns_src.split(':')[-1]

                if not ns_src or ns_src == ':':
                    fake_ns.append(file_ref.refNode)
                    print u"该资产没有命名空间: " + str(file_ref.refNode)
                    continue

                file_path = str(file_ref.path).strip()
                if ns_src != os.path.basename(file_path)[:-3]:
                    fake_ns.append(file_ref.refNode)
                    print u'命名空间与资产名不匹配: '+str(file_ref.refNode)
            except:
                print traceback.format_exc()
                print u"命名空间异常！: " + str(file_ref.refNode)
                fake_ns.append(file_ref.refNode)

        return fake_ns
