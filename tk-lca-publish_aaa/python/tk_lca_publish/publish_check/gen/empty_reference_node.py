# -*- coding:utf-8 -*-

import traceback
import os
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否存在没有和任何.ma文件关联的reference node"
        self.description = u"检查是否存在没有和任何.ma文件关联的reference node"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def isEmptyReferenceNode(self, ref_node):
        try:
            if not ref_node.referenceFile():
                return True
            else:
                return False
        except:
            return None

    def deleteEmptyReferenceNode(self, ref_node):
        try:
            ref_node.unlock()
            pm.delete( ref_node )
            return True
        except:
            return False

    def run_check(self):
        try:
            refNode = pm.ls(rf=True)
            illegal_refNode = []
            for r in refNode:
                if self.isEmptyReferenceNode(r):
                    illegal_refNode.append(str(r))

            if illegal_refNode:
                return u"以下资产reference node没有关联的.ma文件，应该删除:\n" + '\n'.join(illegal_refNode)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            refNode = pm.ls(rf=True)
            failed = []
            for r in refNode[:]:
                if self.isEmptyReferenceNode(r):
                    if not self.deleteEmptyReferenceNode(r):
                        failed.append(str(r))

            if failed:
                return u"以下资产无法被修复命名空间:\n" + '\n'.join(failed)

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

