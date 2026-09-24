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
        self.check_name = u"检查非reference几何体信息。"
        self.description = u"组装资产|master|asb 组下允许有自定义的组，但不可以有非reference几何体信息，不可以与|master|asb之外的物体有约束关系。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            asb = pm.PyNode('|master|asb')
            l_trans = pm.listRelatives('|master|asb', ad=True)

            l_geo = []
            l_geo_node = []
            l_outside = []
            l_assembly_ref = [n.name() for n in pm.ls(type="assemblyReference")]
            for trans in l_trans:
                if pm.referenceQuery( trans, isNodeReferenced=True ):
                    continue

                if trans.name() in l_assembly_ref:
                    continue

                c = pm.container(q=True, findContainer=trans)
                if c and c.name() in l_assembly_ref:
                    continue

                # add fucking exclusion rule for tuk_tuk_bomb, because that rigger add controls in the asb file, this freaky requirement asked by the mad animation
                # let's do this shitty work, fuck everyone
                if os.path.basename(pm.sceneName()).split('.')[0] == 'tuk_tuk_bomb':
                    continue

                #exclude constrains' nodes from rig under master
                if 'Constraint' in trans.type():
                    for j in list(set([i[1] for i in pm.listConnections(trans, c=True, scn=True) if len(i)>1])):
                        if not j.isChildOf(asb):
                            l_outside.append(j.name())

                    continue

                if trans.type() != 'transform':
                    l_geo.append(trans.name())
                    l_geo_node.append(trans)


            if len(l_outside)>0:
                pm.select( clear=True )
                for i in l_outside:
                    j = pm.listRelatives(i,p=True,pa=True,type='transform')
                    if len(j)>0:
                        pm.select(j, add=True)
                return u'发现master以外的物体和内部发生约束关系：\n' + '\n'.join(l_outside)

            if len(l_geo)>0:
                self.l_geo=l_geo_node

                pm.select( clear=True )
                for i in l_geo:
                    j = pm.listRelatives(i,p=True,pa=True,type='transform')
                    if len(j)>0:
                        pm.select(j, add=True)
                return u'发现非reference物体：\n' + '\n'.join(l_geo)

            asb_node = pm.ls('*:asb', r=True, rn=True, long=True)
            if asb_node:
                return u'asb资产不能相互嵌套，找到以下asb资产：\n'+'\n'.join(str(asb_node))

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        try:
            lr=self.l_geo
            for lrr in lr:
                pm.delete(lrr)

            return u"删除了所有非reference物体！"
        except:
            return u"自动修复失败！"



    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


