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
from proc.function_running_time import record_time


# All system check classes will use StdCheck as the class name.
class StdCheck():
    """
        dependency: check_hierarchy
    """
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产reference所属层级。"
        self.description = u"资产reference必须归类到相应的组下，如assembly资产放在scene|scn_asb组下。reference之间不能互为父子层级。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def checkRef(self, masters):
        """
            checkRef(self, l=list)
            referenced nodes under assets group should be in appropriate named group like prp, chr..., return those illegally allocated nodes in a list
        """
        illRef = []
        try:
            for n in masters:
                pathTokens = pm.referenceQuery(n, filename=True).split('/')
                index = 0
                for c in pathTokens:
                    index += 1
                    if c == 'asset' or c == 'assets':
                        break
                if index >= len(pathTokens):
                    illRef.append( str(n)+': illegal reference path' )
                    break
                try:
                    if pm.objExists('|scene|scn_'+pathTokens[index]):
                        if not n.isChildOf( pm.PyNode('|scene|scn_'+pathTokens[index]) ):
                            print str(n)+' should be under |scene|scn_'+pathTokens[index]
                            illRef.append( str(n)+' should be under |scene|scn_'+pathTokens[index] )
                    else:
                        illRef.append( str(n)+' should be under |scene|scn_'+pathTokens[index] )
                except:
                    pass
        except:
            pass

        return illRef

    @record_time(__file__)
    def run_check(self):

        try:
            masters = mru.MayaReferenceUtils().listMasters(top='|scene', asb=False)

            # reference必须归类到正确的组下
            illRef = self.checkRef(masters)
            if len(illRef) > 0:
                return ( u"以下reference节点没有放在正确的组下： \n" + "\n".join([str(c) for c in illRef]) )

            # reference之间不能互为父子层级
            find_illegal_ref = []
            for ref in masters:
                for ref2 in masters:
                    if ref.isParentOf(ref2):
                        find_illegal_ref.append(str(ref))
                        find_illegal_ref.append(str(ref2))
                        break
                if find_illegal_ref:
                    break
            if find_illegal_ref:
                return u"非法的reference层级: "+find_illegal_ref[1]+u"在"+find_illegal_ref[0]+u"层级下。reference之间不能互为父子层级。"

            # Check if there are any referenced asset out of the "|scene" group
            l_master_nodes = pm.ls("*:master")
            l_bad_assets = []

            for node in l_master_nodes:
                if node.isReferenced():
                    if not node.fullPath().startswith('|scene|'):
                        l_bad_assets.append(node.name())

            if len(l_bad_assets) > 0:
                return u"某些资产没有放到 scene 组下: " + u', '.join(l_bad_assets)

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



