# -*- coding: utf-8 -*-
############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: guanzejie
#
# Date: 2022.05
#
# Description:
#
############################################
import maya.standalone
maya.standalone.initialize()
import production.lca_xmpp as lca_xmpp
import maya.cmds as cmds
import sys
import os
OS = sys.platform


def get_version(work_path):

    maya_version = []

    dir_name = os.path.dirname(os.path.dirname(work_path))

    all_version_maya_file = os.listdir(dir_name)

    print(maya_version)
    print(all_version_maya_file)

    if all_version_maya_file:

        for ver in all_version_maya_file:
            if ver[-3:] == ".ma":
                maya_version.append(ver[-6:-3])

        if not maya_version:

            return "001"

        else:

            version_num = str((int(max(maya_version)) + 1))

            if len(version_num) == 1:
                version_num_third = "00" + version_num

            if len(version_num) == 2:
                version_num_third = "0" + version_num

            if len(version_num) == 3:
                version_num_third = version_num

            return version_num_third



def save_to_work_path(maya_name_h1):

    asset_name = maya_name_h1.split("/")[7]
    print asset_name

    asset_name_low = asset_name

    work_path = maya_name_h1############################################################

    version_num = get_version(work_path)

    work_name = os.path.dirname(os.path.dirname(work_path)) + "/" + asset_name_low + ".mod.model.v" + version_num + ".ma"

    print(work_name)

    cmds.file(rename=work_name)
    cmds.file(force=True, save=True, options="v=0", typ="mayaAscii")

    return work_name


# save file to work path
def publish_low(maya_name_h1):

    version_one = save_to_work_path(maya_name_h1)
    print(version_one)

    cmds.file(rename=version_one)

    cmds.file(force=True, save=True, options="v=0", typ="mayaAscii")

    # do publish
    import auto_publish
    reload(auto_publish)
    auto_publish.setup(version_one)

    return 1


def make_low_mod(maya_name_h1,houdini_abc_wa,hi_abc_maya,auto_pu):

    master = cmds.group(em=True, n="master")

    poly = cmds.group(em=True, n="poly", p=master)

    abc1 = cmds.AbcImport(hi_abc_maya, mode="import")
    print(abc1)

    if not houdini_abc_wa == "0":
        abc2 = cmds.AbcImport(houdini_abc_wa, mode="import")
        print(abc2)

    list_tran = cmds.ls(type="transform")
    for i in list_tran:
        print(i)
        if i=="hi":
            cmds.parent("hi",poly)

    list_all_transform = cmds.ls(type="transform")

    for i in list_all_transform:

        if i=="wapian_hi_grp" or i=="wa_hi_grp":

            if "mesh_grp" in list_all_transform:
                cmds.parent(i, "mesh_grp")

    #cmds.file(force=True,save=True,options="v=0")

    nwe_name = maya_name_h1[:-4]+"1.ma"

    print(nwe_name)

    cmds.file(rename=nwe_name)

    cmds.file(force=True, save=True, options="v=0", typ="mayaAscii")

    finish = publish_low(maya_name_h1)

    # if auto_pu == "1":
    #
    #     finish = publish_low(maya_name_h1)
    #
    # if auto_pu == "0":
    #
    #     work_name = save_to_work_path(maya_name_h1)
    #
    #     pidgin_p = lca_xmpp.Sender()
    #     message_p = "已经升级low模版本：path = " + work_name
    #     pidgin_p.send(["zejie","jiantao","haoran"], message_p)
    #
    #     finish = 2

    return finish


print(sys.argv[1])
print(sys.argv[2])
print(sys.argv[3])
print(sys.argv[4])

finish = make_low_mod(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])


if finish == 1:
    pidgin = lca_xmpp.Sender()
    message = 'maya文件提交成功'
    pidgin.send(["zejie","jiantao","haoran"], message)

elif finish == 2:
    pidgin = lca_xmpp.Sender()
    message = '已经升级low模版本'
    pidgin.send(["zejie", "jiantao", "haoran"], message)

else :
    pidgin = lca_xmpp.Sender()
    message = 'maya文件提交失败'
    pidgin.send(["zejie","jiantao","haoran"], message)