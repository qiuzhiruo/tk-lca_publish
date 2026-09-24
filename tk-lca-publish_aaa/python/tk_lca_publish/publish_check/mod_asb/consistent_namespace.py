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
        self.check_name = u"检查每个reference资产必须有命名空间"
        self.description = u"每个reference资产必须有命名空间，并且名字必须与资产名匹配"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

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

    def run_check(self):

        try:
            master = [p.getParent() for p in pm.ls('*poly', r=True, rn=True, long=True) if p.getParent() and 'master' in p.getParent().name()]
            illns = []
            mimic_ns = []
            for m in master:
                refNode = pm.referenceQuery(m, rfn=True)
                if not refNode:
                    continue

                # refNode is a string here
                refNode = pm.PyNode(refNode)

                if refNode.parentNamespace().strip(':') != '':
                    # skip non top reference, cuz we can't change namespace on reference node
                    continue
                ns = self.getNamespace(m)
                if not ns or ns == ':':
                    illns.append(str(m)+' have no namespace, reference must have namespace.')
                else:
                    file_path = pm.referenceQuery(m, filename=True, wcn=True)
                    if ns.strip(':') != os.path.basename(file_path)[:-3]:
                        mimic_ns.append(str(m)+' have different namespace with its filename.')
            if illns:
                return u"发现没有命名空间的reference资产:\n"+'\n'.join(illns)
            if mimic_ns:
                return u"发现命名空间和资产名不匹配:\n"+'\n'.join(mimic_ns)

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


