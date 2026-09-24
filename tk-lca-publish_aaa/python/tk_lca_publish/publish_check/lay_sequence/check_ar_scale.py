# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import sys
import os

import tank
import pymel.core as pm
import pymel.core.datatypes as dt

EXCLUDES = ['lay']

class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查assets下assemblyReference节点的scale属性"
        self.description = u"检查assets下assemblyReference节点的scale属性，保证节点没有被缩放"
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return
    
    def get_top_ARs(self):
        """
        get all top ar nodes under assets
        """
        top_ar_nodes = []
        children = pm.listRelatives('assets', children = True)
        for child in children:
            subChildren = pm.listRelatives(child, children = True)
            for subChild in subChildren:
                if subChild not in EXCLUDES:
                    pass
                    if pm.nodeType(str(subChild)) == 'assemblyReference':
                        pass
                        top_ar_nodes.append(subChild)
        
        #pprint.pprint(top_ar_nodes)
        return top_ar_nodes
    
    def check_scale_value(self, ar_node):
        """
        """
        scale = pm.getAttr(ar_node + '.scale')
        if not scale[0] == scale[1] == scale[2]:
            return False
        return True
    
    def run_check(self):
        try:
            if self.dialog.entity['name'].startswith('z'):
                return u''
            
            top_ar_nodes = self.get_top_ARs()
            invaild_ars = []
            for ar_node in top_ar_nodes:
                result = self.check_scale_value(ar_node)
                if not result:
                    invaild_ars.append(str(ar_node))
            print 'invaild_ars', invaild_ars
            if invaild_ars:
                return u'以下节点的scale属性被改动过：\n' + '\n'.join(invaild_ars)
            else:
                return u''
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



