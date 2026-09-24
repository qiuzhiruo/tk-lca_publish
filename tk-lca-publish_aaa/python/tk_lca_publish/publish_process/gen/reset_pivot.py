# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'



import os
import traceback
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"reset大环(global_ctrl)的旋转和缩放轴心的坐标。"
        self.description = u"reset大环(global_ctrl)的旋转和缩放轴心的坐标。"
        return

    def isAnimation(self, node, animCurveType=['animCurve', 'animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU', 'animCurveUA', 'animCurveUL', 'animCurveUT', 'animCurveUU'], recursive=True ):
        if not recursive:
            anim = pm.listConnections(node, type=animCurveType)
            for a in anim:
                if pm.referenceQuery(a, isNodeReferenced=True):
                    continue
                return True
        else:
            for child in pm.listRelatives(node, ad=True, pa=True, type='nurbsCurve'):
                anim = child.getParent().listConnections(type=animCurveType)
                for a in anim:
                    if pm.referenceQuery(a, isNodeReferenced=True):
                        continue
                    #elif a.isStatic():
                    #    continue
                    #elif a.numKeys() > 1:
                    #    return True
                    return True
        return False

    def isRotationTranslated(self, node):
        try:
            for i in pm.xform(node, query=True, rotateTranslation=True):
                if abs(i) > 0.001:
                    return True
        except:
            pass
        return False

    def proceed(self):
        try:
            masters = [p.getParent() for p in pm.ls('*poly', r=True, long=True, type='transform') if p.getParent() and ':master' in p.getParent().name()]
            for m in masters:
                try:
                    ctrl = m.name().replace(':master', '')+':global_ctrl'
                    if not pm.objExists(ctrl):
                        ctrl = m.name().replace(':master', '')+':intermediate_root_ctrl'
                        if not pm.objExists(ctrl):
                            continue
                    if not self.isAnimation(ctrl, recursive=False):
                        pm.xform(ctrl, zeroTransformPivots=True)
                except:
                    pass

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
