# -*- coding:utf-8 -*-

import os
import traceback
import shutil

import sys

import pymel.core as pm

# sys.path.append('U:/toolset/lib/production/pipeline')
# sys.path.append('/mnt/utility/toolset/lib/production/pipeline')

import production.pipeline.mayaReferenceUtils as mru
reload(mru)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"删除|master|rig"
        self.description = u"删除|master|rig，把master组下的所有大环转换成世界坐标系下，同时删除空组"
        return

    def getTransformation(self, a, space='object'):
        tran = {}
        txyz = a.getTranslation(space=space)
        rxyz = a.getRotation(space=space)
        sxyz = a.getScale()
        tran['tx'] = txyz[0] if a.hasAttr('tx') else None
        tran['ty'] = txyz[1] if a.hasAttr('ty') else None
        tran['tz'] = txyz[2] if a.hasAttr('tz') else None
        tran['rx'] = rxyz[0] if a.hasAttr('rx') else None
        tran['ry'] = rxyz[1] if a.hasAttr('ry') else None
        tran['rz'] = rxyz[2] if a.hasAttr('rz') else None
        tran['sx'] = sxyz[0] if a.hasAttr('sx') else None
        tran['sy'] = sxyz[1] if a.hasAttr('sy') else None
        tran['sz'] = sxyz[2] if a.hasAttr('sz') else None
        tran['globalScale'] = a.attr('globalScale').get() if a.hasAttr('globalScale') else None
        return tran

    def setTransformation(self, a, tran):
        if not tran:
            return
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'globalScale']:
            if a.hasAttr(attr) and tran.has_key(attr) and tran[attr]!=None:
                lockState = a.attr(attr).isLocked()
                if not a.isReferenced():
                    a.setAttr(attr, lock=False)
                try:
                    a.attr(attr).set(tran[attr])
                except:
                    pass
                if not a.isReferenced():
                    a.setAttr(attr, lock=lockState)

    def proceed(self):
        try:
            mref = mru.MayaReferenceUtils()
            masters = mref.listMasters(top='|master')

            # delete intermediate_ctrl
            for m in masters:
                ns = mref.getNamespace(m.name())
                if not pm.objExists(ns+':global_ctrl'):
                    continue

                g_ctrl = pm.PyNode(ns+':global_ctrl')

                if pm.objExists(ns+':intermediate_root_ctrl'):
                    try:
                        node = pm.PyNode(ns+':intermediate_root_ctrl')
                        tran = self.getTransformation( node, 'world' )
                        if pm.objExists(ns+':intermediate_ctrl'):
                            pm.delete( ns+':intermediate_ctrl' )
                        else:
                            pm.delete( node )
                        self.setTransformation(g_ctrl, tran)
                        g_ctrl.getShape().attr('visibility').set(1)
                    except:
                        print traceback.format_exc()

            # delete |master|rig ctrl
            try:
                pm.delete('|master|rig')
            except:
                print traceback.format_exc()

            # delete the empty groups in case of unloading of assets
            try:
                empty_grps = []
                mref.findEmptyGrp('|master',empty_grps)
                pm.delete(empty_grps)
            except:
                print traceback.format_exc()

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


