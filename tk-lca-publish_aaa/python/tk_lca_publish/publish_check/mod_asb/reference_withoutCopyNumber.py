# -*- coding:utf-8 -*-

import traceback
import os
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查reference命名结尾的数字。"
        self.description = u"如果某个资产在场景里只有一次reference，那么其命名空间不可以带数字结尾。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def getNamespace(self, node, wcn=True):
        '''
        get namespace of given node, with leading string ':'
        option: wcn=True, strip tailing number
        '''
        try:
            ns_fn = lambda x: x if x.startswith(':') else ':'+x
            ns = ns_fn( pm.referenceQuery( node, namespace=True ) ).replace(':master', '')
            if wcn:
                # strip tail number
                while ns[-1].isdigit():
                    ns = ns[:-1]
            return ns
        except:
            return ''

    def run_check(self):
        # this check should follow remove_empty_namespace
        try:
            refNode = pm.ls(rf=True)
            illegal_ref = []
            for r in refNode:
                try:
                    if r.parentNamespace().strip(':') != '':
                        # skip non top reference, cuz we can't change namespace on reference node
                        continue

                    file_ref = pm.FileReference(r)
                    if not file_ref.isLoaded():
                        # skip unloaded reference
                        continue

                    if len(file_ref.copyNumberList()) <= 1:
                        if file_ref.namespace.strip(':')[-1].isdigit():
                            # there may be one asset referenced with both of hi and lo version, which produces name with copy number
                            ns = self.getNamespace( r )
                            if pm.namespace( ex=ns ) and pm.objExists(ns+':master'):
                                continue
                            illegal_ref.append( file_ref.fullNamespace.strip(':')+':master' )
                except:
                    pass

            if illegal_ref:
                return u"以下资产只出现一次，但是命名空间带有数字:\n" + '\n'.join(illegal_ref)

            return ""

        except:
            return traceback.format_exc()

    def renameNamespace(self, ns_src, ns_des):
        try:
            pm.namespace(ren=[ns_src, ns_des], f=True)
        except:
            try:
                pm.namespace(ren=[':'+ns_src, ns_des], f=True)
            except:
                try:
                    pm.namespace(ren=[ns_src, ':'+ns_des], f=True)
                except:
                    try:
                        pm.namespace(ren=[':'+ns_src, ':'+ns_des], f=True)
                    except:
                        return False
        return True

    def run_fix(self):
        '''Auto Fix'''
        try:
            refNode = pm.ls(rf=True)
            illegal_ref = []
            for r in refNode:
                if r.parentNamespace().strip(':') != '':
                    # skip non top reference, cuz we can't change namespace on reference node
                    continue
                file_ref = pm.FileReference(r)
                ns_src = file_ref.fullNamespace.strip(':')
                if len(file_ref.copyNumberList()) <= 1:
                    if ns_src[-1].isdigit():
                        # delete namespace without copy number
                        ns_des = self.getNamespace(r).strip(':')
                        if not ns_des:
                            print 'failed to get namespace: '+str(r)
                            illegal_ref.append( str(r) )
                            continue
                        if pm.namespace(ex=ns_des):
                            if pm.Namespace(ns_des).listNodes():
                                try:
                                    self.renameNamespace(ns_des, ns_des+'_bak')
                                except:
                                    # unable to rename namespace
                                    traceback.print_exc()
                                    illegal_ref.append( ns_src+':master' )
                                continue
                            else:
                                # do deletion
                                try:
                                    pm.namespace(remove=ns_des)
                                except:
                                    print 'failed to delete namespace: '+ns_des
                                    illegal_ref.append( ns_src+':master' )
                                    continue
                        # shift current namespace to destination
                        try:
                            self.renameNamespace(ns_src, ns_des)
                        except:
                            print 'failed to rename namespace: '+ns_src+':master, try to remove the reference asset and create it again.'
                            illegal_ref.append( ns_src+':master' )
                            continue

            if illegal_ref:
                return u"以下资产无法被修复命名空间:\n" + '\n'.join(illegal_ref)

            return ""

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

