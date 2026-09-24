# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.01
#
# Description: As the description shows below
#
############################################

import os
import traceback
import pymel.core as pm
import xml.etree.ElementTree

import production.decorators
import production.mayautils as mutils
import ani.lca_t_pose.functions as functions
import ani.lca_layer_manager.functions as functions2
import gene.scene_operator.sceneOperator as sceneOperator
reload(sceneOperator)

ASSET_SELECTOR = 'asset_selector'
GLOBAL_CONTROLS = ('global_ctrl', 'intermediate_root_ctrl', 'intermediate_ctrl')


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产锁定状态。"
        self.description = u"为了避免输出不必要的缓存，没有修改的资产需要保持锁定状态。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            self.invalid_assets = []
            selectors = pm.general.ls(ASSET_SELECTOR,
                                      recursive=True,
                                      referencedNodes=True)
            for selector in mutils.progressIter(selectors,
                                                status=self.get_check_name(),
                                                isInterruptable=False):
                if False:
                    isinstance(selector, pm.nt.Transform)

                # skip locked assets
                if not selector.hasAttr('activated'):
                    continue

                if not selector.attr('activated').get():
                    continue

                # check attrs on non-global controls
                ctrls = functions.getControlsFromNode(selector)
                if isControlsModified(ctrls, ignore_list=GLOBAL_CONTROLS):
                    continue

                ref = selector.referenceFile()
                parent = pm.system.referenceQuery(ref, parent=True, referenceNode=True)
                namespace = selector.namespaceList()[-1]

                # inside asb or scn, compare with scene graph xml
                if parent:
                    path = pm.system.referenceQuery(ref, parent=True, filename=True)
                    sgxml = sg_xml_from_ma(path)
                    if not os.path.isfile(sgxml):
                        print 'Scene Graph XML not found:', sgxml, 'skipping...'
                        continue

                    data = get_data_from_sg_xml(sgxml)
                    xform = data.get(namespace)
                    if not xform:
                        print 'Matrix info not found for asset:', namespace, 'in xml:', sgxml
                        continue

                    ctrl = selector.namespace() + GLOBAL_CONTROLS[1]
                    if not pm.general.objExists(ctrl):
                        print 'Control not found:', ctrl
                        continue

                    ctrl = pm.nt.Transform(ctrl)
                    matrix = pm.general.xform(ctrl, query=True, matrix=True, objectSpace=True)
                    if not xform == ' '.join(str(i) for i in matrix):
                        continue

                # top-level asset, check also global controls
                elif isControlsModified(ctrls):
                    continue

                master = functions2.getMasterFromSelector(selector)
                self.invalid_assets.append(master)

            if self.invalid_assets:
                pm.general.select(self.invalid_assets)
                return u'以下资产并未改动，需要重新锁定：\n'+'\n'.join(str(i) for i in self.invalid_assets)

            return ''

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        if self.invalid_assets:
            aa = sceneOperator.AssetsActivator2()
            aa.deactivate(self.invalid_assets, force=True)
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


@production.decorators.memoize
def sg_xml_from_ma(path):
    dirname, basename = os.path.split(path)
    xmlbase = os.path.splitext(basename)[0] + '.xml'
    xmlpath = os.path.join(dirname, 'scene_graph_xml', xmlbase)
    return xmlpath


@production.decorators.memoize
def get_data_from_sg_xml(path):
    tree = xml.etree.ElementTree.parse(path)
    root = tree.getroot()
    result = dict()
    instances = root.getiterator("instance")
    for i in instances:
        name = i.attrib['name']
        xform = i.find('xform')
        if xform is None:
            continue

        value = xform.attrib.get('value')
        if value is None:
            continue

        result.setdefault(name, value)

    return result


def isControlsModified(ctrls, ignore_list=[]):
    for ctrl in ctrls:
        if False:
            isinstance(ctrl, pm.nt.Transform)

        ctrl_short = ctrl.stripNamespace()
        if ctrl_short in ignore_list:
            continue

        attrs = ctrl.listAnimatable()
        for attr in attrs:
            if False:
                isinstance(attr, pm.general.Attribute)

            if not attr.isFreeToChange():
                continue

            curves = attr.inputs(type='animCurve')
            if curves and not curves[0].isReferenced():
                return True

            current = attr.get()
            defaults = pm.general.attributeQuery(attr.attrName(),
                                                 node=attr.nodeName(),
                                                 listDefault=True)
            if not round(current, 4) == defaults[0]:
                return True

    return False
