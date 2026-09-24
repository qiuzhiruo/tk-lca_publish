# -*- coding:utf-8 -*-

import os
import traceback
import pymel.core as pm
import maya.cmds as mc
import math
import shutil
import os
import glob
import random
import json
import production.python_job as ppj
import getpass
from production.shotgun_connection import Connection
sg = Connection('get_project_info').get_sg()


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"随机拼装 Pass 组合输出下游，渲染 facePass 预览"
        self.description = u"随机拼装 Pass 组合输出下游，渲染 facePass 预览"
        return

    def proceed(self):
        try:
            try:
                render_code(self.dialog)

            except:
                print traceback.format_exc()

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description


def render_code(dialog):
    if not mc.objExists("visibility_ctrl.facePass"): # 没有 facePass 直接返回
        return

    crd_face_pass_tag = False # 判断sg 上资产的标签里是否有 “crd_face_pass”
    asset = sg.find_one("Asset", [["code", "is", "td_test_rig_crd"]], ["id", "code", "tags"])
    if asset:
        tags = asset.get("tags", [])
        tags_array = []
        for tag in tags:
            tags_array.append(tag["name"])
        if "crd_face_pass" in tags_array:
            crd_face_pass_tag = True


    preview_dir = dialog.version_dir + '/facePass_render/'  # 创建渲染的文件夹
    if not os.path.isdir(preview_dir):
        os.makedirs(preview_dir)

    mc.setAttr("defaultRenderGlobals.imageFormat", 32)
    mc.workspace(fileRule=['images', preview_dir])


    body_cam_path, body_cam, head_cam_path, head_cam = reference_cameras()   # 拿进来相机

    light = create_light()    # 创建灯光


    if crd_face_pass_tag == False: # 如果没有标签 说明是chr
        facePass_enum_tab_array = getEnum("facePass")
        iter_v = None
        for i, enum_tab in enumerate(facePass_enum_tab_array):
            mc.setAttr("{}.{}".format("visibility_ctrl", "facePass"), i)

            if mc.objExists("head_M_ctrl"):  # 将head_cam 设置到正确的位置上
                v = mc.xform("head_M_ctrl", q=True, ws=True, t=True)[1]
                if iter_v != None:
                    set_v = v - iter_v
                    head_cam_tr = mc.listRelatives(head_cam, p=True)[0]
                    mc.xform(head_cam_tr, t=(0, set_v, 0), r=True)
                    mc.refresh()
                iter_v = v

            mc.setAttr("defaultRenderGlobals.imageFilePrefix", "{}.head.rig".format(enum_tab), type="string")
            mc.render(head_cam, x=1024, y=1024)

            mc.setAttr("defaultRenderGlobals.imageFilePrefix", "{}.body.rig".format(enum_tab), type="string")
            mc.render(body_cam, x=1024, y=1024)

    else:  # 如果有标签 说明是crd
        print "--------------------------------------------------------------------------"
        facePass_enum_orig_array = getEnum("facePass")
        rigPass_enum_orig_array = getEnum("rigPass")
        headHair_enum_orig_array = getEnum("headHair")


        facePass_enum_tab_array = facePass_enum_orig_array[:]
        rigPass_enum_tab_array = rigPass_enum_orig_array[:]
        headHair_enum_tab_array = headHair_enum_orig_array[:]


        facePass_enum_tab_array.remove("default")
        # rigPass_enum_tab_array.remove("default")
        # headHair_enum_tab_array.remove("default")

        long_hair_info = False
        if "long" in headHair_enum_tab_array:
            headHair_enum_tab_array.remove("long")
            long_hair_info = True


        count_array = [len(facePass_enum_tab_array), len(rigPass_enum_tab_array), len(headHair_enum_tab_array)]
        count_array.sort(reverse=1)

        facePass_array = []
        rigPass_array = []
        headHair_array = []

        for i in range(count_array[0]): # 遍历次数按照 以上pass 数量的最大值， 先按顺序添加每个pass index，多出来的随机这些pass index

            if len(facePass_enum_tab_array) == 0:  # facePass
                pass_index = None
            elif i < len(facePass_enum_tab_array):
                pass_index = i
            else:
                index = random.randint(0, len(facePass_enum_tab_array) - 1)
                pass_index = index
            if pass_index != None:
                facePass_array.append(facePass_enum_tab_array[pass_index])
            else:
                facePass_array.append(None)


            if len(rigPass_enum_tab_array) == 0:  # rigPass
                pass_index = None
            elif i < len(rigPass_enum_tab_array):
                pass_index = i
            else:
                index = random.randint(0, len(rigPass_enum_tab_array) - 1)
                pass_index = index
            if pass_index != None:
                rigPass_array.append(rigPass_enum_tab_array[pass_index])
            else:
                rigPass_array.append(None)


            if len(headHair_enum_tab_array) == 0:  # headHair
                pass_index = None
            elif i < len(headHair_enum_tab_array):
                pass_index = i
            else:
                index = random.randint(0, len(headHair_enum_tab_array) - 1)
                pass_index = index
            if pass_index != None:
                headHair_array.append(headHair_enum_tab_array[pass_index])
            else:
                headHair_array.append(None)


        # random.shuffle(facePass_array)
        random.shuffle(rigPass_array)
        random.shuffle(headHair_array)



        past_json_data = find_past_json(dialog)

        enum_info = {"facePass": facePass_enum_orig_array,
                     "rigPass": rigPass_enum_orig_array,
                     "headHair": headHair_enum_orig_array}
        basic_pass_combin_info = zip(facePass_array, rigPass_array, headHair_array)
        long_pass_combin_info = []
        if long_hair_info:
            long_pass_combin_info = zip(facePass_array, rigPass_array, ["long" for i in range(len(facePass_array))])
        current_json_data = {"enum_info": enum_info,
                             "combin_info": {"basic": basic_pass_combin_info, "long": long_pass_combin_info}}

        if past_json_data["enum_info"] == current_json_data["enum_info"]:
            render_json = past_json_data
            print("the same, copy data")
        else:
            render_json = current_json_data
            print("different, export data")

        export_json_info(dialog, render_json)
        mc.dgdirty("visibility_ctrl")
        # ================================================= render ==================================================
        image_index = 1
        for facePass, rigPass, headHair in render_json["combin_info"]["basic"]:

            if facePass in facePass_enum_orig_array:
                facePass_index = facePass_enum_orig_array.index(facePass)
                mc.setAttr("{}.{}".format("visibility_ctrl", "facePass"), facePass_index)

            if rigPass in rigPass_enum_orig_array:
                rigPass_index = rigPass_enum_orig_array.index(rigPass)
                mc.setAttr("{}.{}".format("visibility_ctrl", "rigPass"), rigPass_index)

            if headHair in headHair_enum_orig_array:
                headHair_index = headHair_enum_orig_array.index(headHair)
                mc.setAttr("{}.{}".format("visibility_ctrl", "headHair"), headHair_index)

            mc.setAttr("defaultRenderGlobals.imageFilePrefix",
                       "FACEPASS_{}_{}_{}_{}.head.rig".format(image_index, facePass, rigPass, headHair),
                       type="string")
            render(head_cam)
            image_index += 1

        if long_hair_info: # 如有长发
            for facePass, rigPass, headHair in render_json["combin_info"]["long"]:

                if facePass in facePass_enum_orig_array:
                    facePass_index = facePass_enum_orig_array.index(facePass)
                    mc.setAttr("{}.{}".format("visibility_ctrl", "facePass"), facePass_index)

                if rigPass in rigPass_enum_orig_array:
                    rigPass_index = rigPass_enum_orig_array.index(rigPass)
                    mc.setAttr("{}.{}".format("visibility_ctrl", "rigPass"), rigPass_index)

                if headHair in headHair_enum_orig_array:
                    headHair_index = headHair_enum_orig_array.index(headHair)
                    mc.setAttr("{}.{}".format("visibility_ctrl", "headHair"), headHair_index)

                mc.setAttr("defaultRenderGlobals.imageFilePrefix",
                           "FACEPASS_{}_{}_{}_{}.head.rig".format(image_index, facePass, rigPass, headHair),
                           type="string")
                render(head_cam)
                image_index += 1

        #  pass zero
        if mc.objExists("{}.{}".format("visibility_ctrl", "facePass")):
            mc.setAttr("{}.{}".format("visibility_ctrl", "facePass"), 0)
        if mc.objExists("{}.{}".format("visibility_ctrl", "rigPass")):
            mc.setAttr("{}.{}".format("visibility_ctrl", "rigPass"), 0)
        if mc.objExists("{}.{}".format("visibility_ctrl", "headHair")):
            mc.setAttr("{}.{}".format("visibility_ctrl", "headHair"), 0)


        # ================================================= render ==================================================


    mc.delete(light)

    mc.file(body_cam_path, removeReference=True)
    mc.file(head_cam_path, removeReference=True)

    # move_png_to_root(preview_dir)
    project_name = dialog.project['name'].lower()
    asset_name = dialog.entity['name'].lower()
    task_name = dialog.task['name'].lower()
    asset_step = dialog.step['name']
    user_name = dialog.user['name']

    linuxPath = os.path.normpath(
        os.path.join("/mnt/proj/projects", preview_dir.split("/projects/")[-1])).replace("\\", "/")

    # window 机器路径发送农场（linux）找不到路径
    # py_code = os.getenv('LCA_PUBLISH_APP') + "/python/tk_lca_publish/publish_process/rig/facePass_combined.py"
    py_code = r"/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/rig/facePass_combined.py"
    # py_code = r"/mnt/work/shome/wangqi2/code/facePass_combined.py" # 测试路径

    ppj.send_job(py_code,
                 args=" ".join([linuxPath, project_name, asset_name, "rig", "rig", getpass.getuser()]),
                 proj=project_name,
                 user=getpass.getuser(),
                 pools='common',
                 priority=8000,
                 step='ple',
                 output_list=[],  # 需要解除权限的路径放进去  '/mnt/work/shome/wangqi2/test'
                 job_name_prefix="RIGGING_render_combined_{}".format(asset_name),
                 python_exe='/mnt/utility/linked_tools/lca_rez/launchers/sgl/linux/mayapy2019')



def render(cam):
    for side in ["L", "R"]:
        mc.setAttr("eyelid_{}_up_all_ctrl.translateY".format(side), 0.5)
        mc.setAttr("eyelid_{}_dn_all_ctrl.translateY".format(side), -0.5)
    mc.setAttr("shape.visibility", 0)

    mc.render(cam, x=1024, y=1024)

    for side in ["L", "R"]:
        mc.setAttr("eyelid_{}_up_all_ctrl.translateY".format(side), 0)
        mc.setAttr("eyelid_{}_dn_all_ctrl.translateY".format(side), 0)


def find_past_json(dialog):
    json_path = dialog.version_dir + '/facePass_combin_info.json'

    # 获取上一版的facePass json 路径
    first_path, version_value = dialog.version_dir.split("rigging.v")

    iter_v = int(version_value)
    past_json_path = ""
    while iter_v != 1:
        iter_v -= 1
        past_json_path = first_path + "rigging.v" + str(iter_v).zfill(3) + '/facePass_combin_info.json'
        if os.path.isfile(past_json_path):
            break

    print "current  version : {} ".format(json_path)
    print "get past  version : {} ".format(past_json_path)

    # 如果有这个json 就获取内容
    past_version_data = {"enum_info": None, "combin_info": None}
    if os.path.isfile(past_json_path):
        with open(past_json_path, "r") as f:
            data = json.load(f)
            past_version_data = data
    print "past_version_data"
    print past_version_data
    return past_version_data


def export_json_info(dialog, data):
    json_path = dialog.version_dir + '/facePass_combin_info.json'
    with open(json_path, "w") as f:
        json.dump(data, f)
    print "success export facePass json info"



def getEnum(attr="facePass"):
    enum_tab_array = []
    if mc.objExists("{}.{}".format("visibility_ctrl", attr)):
        enum_str = mc.addAttr("{}.{}".format("visibility_ctrl", attr), q=True, en=True)
        enum_tab_array = ["{}".format(i) for i in filter(None, enum_str.split(":"))]
    return enum_tab_array



def move_png_to_root(folder):
    for dirpath, _, filenames in os.walk(folder):
        if dirpath != folder:
            for f in filenames:
                if f.endswith('.png'):
                    shutil.move(os.path.join(dirpath, f), os.path.join(folder, f))
    tmp_path = os.path.join(folder, 'tmp')
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)


def create_light():
    light_main = mc.directionalLight(name="SunLight")
    light_main_tr = mc.listRelatives(light_main, p=True)[0]
    mc.setAttr("{}.r".format(light_main_tr), -31.522, -9.093, 33.078, type="double3")
    mc.setAttr("{}.intensity".format(light_main_tr), 1.4)
    mc.setAttr("{}.useDepthMapShadows".format(light_main), 1)
    mc.setAttr("{}.dmapResolution".format(light_main), 2048)

    light_sec = mc.directionalLight(name="SunLight")
    light_sec_tr = mc.listRelatives(light_sec, p=True)[0]
    mc.setAttr("{}.r".format(light_sec_tr), 4.188, 50.603, 19.183, type="double3")
    mc.setAttr("{}.intensity".format(light_sec_tr), 0.9)

    light_back = mc.directionalLight(name="SunLight")
    light_back_tr = mc.listRelatives(light_back, p=True)[0]
    mc.setAttr("{}.r".format(light_back_tr), -213.817, 58.196, -123.894, type="double3")
    mc.setAttr("{}.intensity".format(light_back_tr), 0.5)

    return light_main_tr, light_sec_tr, light_back_tr


def reference_cameras():
    file_path = mc.file(q=True, sn=True)
    if not file_path:
        if mc.objExists("master.rigPath"):
            file_path = mc.getAttr("master.rigPath")
    file_path = file_path.replace("W:", "Z:")

    front_path = file_path.split("/rig/")[0]
    chr_name = front_path.split("/")[-1]

    camera_fol = os.path.join(front_path, "mod", "publish", chr_name + ".mod.model", "turntable_cam").replace("\\", "/")

    body_cam_path = os.path.join(camera_fol, "body_cam.abc").replace("\\", "/")
    head_cam_path = os.path.join(camera_fol, "head_cam.abc").replace("\\", "/")

    mc.file(body_cam_path, ignoreVersion=1, type="Alembic", namespace="body_cam", r=1, gl=1,
            mergeNamespacesOnClash=False)
    mc.file(head_cam_path, ignoreVersion=1, type="Alembic", namespace="head_cam", r=1, gl=1,
            mergeNamespacesOnClash=False)

    body_ref_node = mc.referenceQuery(body_cam_path, referenceNode=True)
    head_ref_node = mc.referenceQuery(head_cam_path, referenceNode=True)

    body_camera = mc.ls(mc.referenceQuery(body_ref_node, nodes=True), type="camera")[0]
    head_camera = mc.ls(mc.referenceQuery(head_ref_node, nodes=True), type="camera")[0]

    return body_cam_path, body_camera, head_cam_path, head_camera


if __name__ == '__main__':
    # render_code()
    pass







