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

from proc.function_running_time import record_time



class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查每个reference资产必须有命名空间, 且名字必须与资产名匹配"
        self.description = u"每个reference资产必须有命名空间，并且名字必须与资产名匹配"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def getNamespace(self, node, wcn=True):
        try:
            ns_fn = lambda x: x if x.startswith(':') else ':'+x
            ns = ns_fn( pm.referenceQuery( node, namespace=True ) ).replace(':master', '')
            if wcn:
                # strip tail number
                while ns[-1].isdigit():
                    ns = ns[:-1]
            return ns
        except:
            return None

    @record_time(__file__)
    def run_check(self):

        try:
            utils = mru.MayaReferenceUtils()
            master = utils.listMasters(top='|scene', asb=False)
            illns = []
            mimic_ns = []
            for m in master:
                file_ref = utils.getReferenceFile(m)
                ns = self.getNamespace(file_ref)
                if not ns or ns == ':':
                    illns.append(str(m)+' have no namespace, reference must have namespace.')
                else:
                    if not ns.strip(':') in file_ref.path:
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


