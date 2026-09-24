# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.02
#
# Description: 
#
############################################

import traceback

import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查多余的命名空间。"
        self.description = u"单独资产文件不带任何命名空间。有Reference的文件不带额外的命名空间。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            l_ns = pm.namespaceInfo(listOnlyNamespaces=True)
            l_extra_ns = []

            for ns in l_ns:
                if ns in [u'UI', u'shared']:
                    continue

                if pm.objExists(ns+':master'):
                    if pm.referenceQuery(ns+':master', isNodeReferenced=True):
                        continue
                    if pm.container( findContainer=ns+':master', q=True):
                        continue

                ref_ns = False
                for n in pm.namespaceInfo(ns, listOnlyDependencyNodes=True):
                    nodeType=pm.mel.eval('nodeType "%s"'%n.name())
                    if nodeType in ['assemblyReference', 'gpuCache']:
                        ref_ns = True
                        break

                    if pm.referenceQuery(n, isNodeReferenced=True):
                        ref_ns = True
                        break

                if not ref_ns:
                    l_extra_ns.append(ns)

            if len(l_extra_ns) > 0:
                return u'发现命名空间:\n' + '\n'.join(l_extra_ns)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            l_new_ns = pm.namespaceInfo(listOnlyNamespaces=True, recurse=True)
            l_all_ns = pm.namespaceInfo(listOnlyNamespaces=True, recurse=True)
            l_all_ns.append('')
            l_ref_ns = []

            while len(l_all_ns) > len(l_new_ns):
                l_all_ns = l_new_ns
                l_top_ns = pm.namespaceInfo(listOnlyNamespaces=True)
                for ns in l_top_ns:
                    if ns in [u'UI', u'shared']:
                        continue
                    if ns in l_ref_ns:
                        continue

                    # Get reference namespaces
                    if pm.objExists(ns+':master'):
                        if pm.referenceQuery(ns+':master', isNodeReferenced=True):
                            l_ref_ns.append(ns)
                            continue
                        
                    for n in pm.namespaceInfo(ns, listOnlyDependencyNodes=True):
                        nodeType=pm.mel.eval('nodeType "%s"'%n.name())
                        if nodeType in ['assemblyReference']:
                            l_ref_ns.append(ns)
                            break

                        if pm.referenceQuery(n, isNodeReferenced=True):
                            l_ref_ns.append(ns)
                            break
                            
                    if ns in l_ref_ns:
                        continue                   

                    # Remove redundant namespaces
                    try:
                        pm.namespace( f=True, moveNamespace=(ns, ":"))
                        pm.namespace(removeNamespace = ns )
                        print 'Remove namespace:', ns
                    except:
                        pass
                l_new_ns = pm.namespaceInfo(listOnlyNamespaces=True, recurse=True)

            return ''

        except:
            return traceback.format_exc()

        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


