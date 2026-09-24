# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: No referenced nodes under |master.
#
########################################################################################

import re
import traceback
import pymel.core as pm
import maya.cmds as mc


def extra_listRelatives(obj):
    if isinstance(obj, list):
        child_array = []
        for i in obj:
            try:
                child = mc.listRelatives(i)
                if not child == None:
                    for c in child:
                        child_array.append(c)
            except:
                pass
        return child_array


def find_Tree(obj):
    result = mc.listRelatives(obj)
    if result == None:
        result = []
        return result
    result = result + find_Tree(result)
    return result


def get_parentVis(obj):
    fullName = mc.ls(obj, long=True)[0]
    strArray = filter(None, fullName.split("|"))
    for i in strArray:
        if False == mc.getAttr("{}.v".format(i)):
            return False
    return True


def check_sameName(result):
    error = []
    for i in mc.ls():
        if "|" in str(i):
            error.append(i)
    if error:
        result[0] = u"命名冲突：{}".format(error)
        return True
    return False

def check_ShapeDeformed(result):
    child_array = find_Tree(mc.ls("*:poly"))
    error = []
    for i in child_array:
        if "mesh" == mc.nodeType(i):

            if mc.referenceQuery(i, isNodeReferenced=True):
                continue

            parent_name = mc.listRelatives(i, p=True)[0]

            if "Shape" in i:
                name = parent_name.split(":")[-1]
                array_shape = filter(None, i.split("Shape"))

                if name == array_shape[0] or parent_name == array_shape[0]:
                    if len(array_shape) == 1:
                        continue

                    if len(array_shape) == 2:
                        if "Orig" in array_shape[1]:
                            continue

                        else:
                            error.append(i)
                            continue
                    else:
                        error.append(i)
                        continue
                else:
                    error.append(i)
                    continue
            else:
                error.append(i)
                continue

    if error:
        result[0] = u"错误命名的Shape节点：{}".format(error)
        return True

    return False


def check_rigGroupMeshVis(result):
    error_mesh = []
    child_array = find_Tree(["rig"])
    for i in child_array:
        if "mesh" == mc.nodeType(i):
            if get_parentVis(i):
                error_mesh.append(i)
    if not len(error_mesh) == 0:
        result[0] = u"不该显示的Mesh：{}".format(error_mesh)
        return True
    return False


def check_top_group(result):
    filter_obj = [u'front', u'master', u'persp', u'side', u'top']
    array = []
    for i in mc.ls(type="transform"):
        parent_V = mc.listRelatives(i, p=True)
        if parent_V == None:
            array.append(i)

    error_obj = []
    for i in array:
        if not i in filter_obj:
            error_obj.append(i)

    if not len(error_obj) == 0:
        result[0] = u"大纲顶部错误：{}".format(error_obj)
        return True

    return False


def check_nameSpace(result):
    refNode = pm.listReferences()
    error_result = []
    for i in refNode:
        path = i.path
        nameSpace = i.namespace
        fileName = path.split("/")[-1].split(".")[0]
        pattern = r"^{}[0-9]*$".format(fileName)
        if not re.match(pattern, nameSpace):
            error_result.append(nameSpace)

    if error_result:
        info = ""
        for i in error_result:
            info += i
            info += ", "
        result[0] = "NameSpace Error: ({})".format(info)
        return True

    return False


def check_level(result):
    poly_grp = mc.ls("*:poly")
    for i in poly_grp:
        fullPath = mc.ls(i, long=True)[0]
        fullPath_str_Array = fullPath.split("|")

        if not "master" in fullPath_str_Array:
            result[0] = u"层级有问题 请检查"
            return True

        if not "rra" in fullPath_str_Array:
            result[0] = u"层级有问题 请检查"
            return True

    return False




# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"rra 场景检查"
        self.description = u"rra 场景检查"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        result = [None]
        try:
            if check_sameName(result):
                return u"Error: {}".format(result[0])

            if check_ShapeDeformed(result):
                return u"Error: {}".format(result[0])

            if check_rigGroupMeshVis(result):
                return u"Error: {}".format(result[0])

            if check_top_group(result):
                return u"Error: {}".format(result[0])

            if check_nameSpace(result):
                return u"Error: {}".format(result[0])

            if check_level(result):
                return u"Error: {}".format(result[0])

            return ""


        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        pass


    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty


if __name__ == '__main__':
    cls = StdCheck(0)
    print cls.run_check()
