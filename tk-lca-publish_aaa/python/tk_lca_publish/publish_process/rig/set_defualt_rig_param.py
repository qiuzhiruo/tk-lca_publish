# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.05
#
# Description: 
#
############################################
import os
import traceback
import shutil
import pymel.core as pm
from sgtk.platform.qt import QtGui
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om


class find_source():
    def __init__(self, node_name):
        self.l_processed_nodes = []
        self.l_terminals = []
        self.l_history_nodes = [n.name() for n in pm.listHistory(node_name)]
        self.find_in_mesh(node_name)
        return

    def find_in_mesh(self, node_name):
        self.l_processed_nodes.append(node_name)
        l_in_meshes = []
        l_cons = pm.listConnections(node_name, d=False, s=True, c=True, p=True)

        for con in l_cons:
            att_type = pm.getAttr(con[0], type=True)
            if att_type == 'mesh':
                src_name = con[1].split('.')[0]
                l_in_meshes.append(src_name)

        l_in_meshes = list(set(l_in_meshes))
        if len(l_in_meshes) == 0 and node_name in self.l_history_nodes:
            self.l_terminals.append(node_name)
        else:
            for src_name in l_in_meshes:
                if not src_name in self.l_processed_nodes:
                    self.find_in_mesh(src_name)

        return

def lsUnConnectedAttrId(bakeattrs='master.bakeAttrs'):
    id=0
    cas=cmds.listConnections(bakeattrs+'['+str(id)+']',s=1,d=0,p=1)
    while cas:
        id=id+1
        cas=cmds.listConnections(bakeattrs+'['+str(id)+']',s=1,d=0,p=1)
    return id


def set_attr_value(attr,v):
    try:
        cmds.setAttr(attr,v)
    except:
        None

def get_custom_attributes(node):

    all_attrs = cmds.listAttr(node, userDefined=True, settable=True) or []
    for attr in all_attrs:
        if cmds.attributeQuery(attr, node=node, exists=True):
            if 'ctrl_vis' in attr:
                try:
                    cmds.setAttr(node + '.' + attr, 0)
                except:
                    pass
    return

def set_vis_attr():
    all_ctrls = cmds.ls("*_ctrl")

    for each in all_ctrls:
        custom_attrs = get_custom_attributes(each)

def sync_proxy_visibility(
        proxy_grp="proxy",
        shape_grp="shape"
):
    """
    同步 proxy_组 mesh 到 shape组正式模型的显示隐藏
    """

    # 检查组
    if not cmds.objExists(proxy_grp):
        cmds.warning(u"不存在组: {}".format(proxy_grp))
        return

    if not cmds.objExists(shape_grp):
        cmds.warning(u"不存在组: {}".format(shape_grp))
        return


    # 获取proxy下面所有mesh shape
    proxy_mesh_shapes = cmds.listRelatives(
        proxy_grp,
        ad=True,
        type="mesh",
        fullPath=True
    )

    if not proxy_mesh_shapes:
        cmds.warning(u"proxy has no mesh")
        return


    for proxy_shape in proxy_mesh_shapes:

        # 获取transform
        proxy_transform = cmds.listRelatives(
            proxy_shape,
            parent=True,
            fullPath=True
        )[0]


        proxy_name = proxy_transform.split("|")[-1]


        # 去掉proxy_前缀
        if not proxy_name.startswith("proxy_"):
            continue

        real_name = proxy_name.replace("proxy_", "", 1)


        # 正式模型路径
        real_obj = None

        children = cmds.listRelatives(
            shape_grp,
            children=True,
            type="transform",
            ad=True
        )

        if children:
            for c in children:
                if c.split("|")[-1] == real_name:
                    real_obj = c
                    break


        if not real_obj:
            print(
                u"cannot find mesh:",
                real_name
            )
            continue


        # -------------------------
        # 获取proxy visibility
        # -------------------------

        vis_attr = proxy_transform + ".visibility"


        # 检查是否有连接
        connections = cmds.listConnections(
            vis_attr,
            source=True,
            destination=False
        )

        if connections:
            print(
                u"skip visibility connections:",
                proxy_name
            )
            continue


        # 如果锁定，解锁
        if cmds.getAttr(vis_attr, lock=True):
            cmds.setAttr(
                vis_attr,
                lock=False
            )


        # 当前proxy显示状态
        proxy_vis = cmds.getAttr(vis_attr)


        # 同步正式模型
        real_vis_attr = real_obj + ".visibility"


        # 如果正式模型属性被锁，也解锁
        try:
            if cmds.getAttr(real_vis_attr, lock=True):
                cmds.setAttr(
                    real_vis_attr,
                    lock=False
                )


            # 如果正式模型有连接，不修改
            real_connections = cmds.listConnections(
                real_vis_attr,
                source=True,
                destination=False
            )

            if real_connections:
                print(
                    u"right visibility is connected, skip:",
                    real_name
                )
                continue


            cmds.setAttr(
                real_vis_attr,
                proxy_vis
            )


            print(
                u"sync finished:",
                proxy_name,
                "->",
                real_name,
                proxy_vis
            )
        except:
            pass

def set_defualt_rig_param(proj, asset):
    # set vis_ctrl attribute
    set_vis_attr()

    set_attr_value('visibility_ctrl.proxy_vis',1)
    set_attr_value('visibility_ctrl.proxy_type_vis',0)
    set_attr_value('facial_panel',0)
    set_attr_value('visibility_ctrl.mesh_display_type',2)
    set_attr_value('visibility_ctrl.anim_rig_vis',0)
    set_attr_value('visibility_ctrl.tech_rig_vis',1)
    set_attr_value('visibility_ctrl.facial_rig_state',0)
    set_attr_value('visibility_ctrl.special_deformer_state',1)
    set_attr_value('visibility_ctrl.facial_panel',0)
    try:
        cmds.setAttr("eyelid_L_aim_1_ctrl.pupil", keyable=True)
        cmds.setAttr("eyelid_L_aim_1_ctrl.iris", keyable=True)
        cmds.setAttr("eyelid_L_aim_1_ctrl.sharp", keyable=True)
        cmds.setAttr("eyelid_L_aim_1_ctrl.eyelid_follow", keyable=True)
        cmds.setAttr("eyelid_R_aim_1_ctrl.pupil", keyable=True)
        cmds.setAttr("eyelid_R_aim_1_ctrl.iris", keyable=True)
        cmds.setAttr("eyelid_R_aim_1_ctrl.sharp", keyable=True)
        cmds.setAttr("eyelid_R_aim_1_ctrl.eyelid_follow", keyable=True)
    except:
        pass

    attr_list = [["mouth_R_1_ctrl.naso_ctrl_vis",0],
    ["mouth_L_1_ctrl.naso_ctrl_vis",0],
    ["nasolabial_R_1_ctrl.lower_zip",0],
    ["nasolabial_R_1_ctrl.upper_zip",0],
    ["nasolabial_L_1_ctrl.upper_zip",0],
    ["nasolabial_L_1_ctrl.lower_zip",0],
    ["nasolabial_L_1_ctrl.mouth_L_1_ctrl",1],
    ["nasolabial_R_1_ctrl.mouth_R_1_ctrl",1],
    ["mouth_M_up_all_ctrl.sec_ctrl_vis",1],
    ["mouth_M_up_all_ctrl.naso_ctrl_vis",0],
    ["mouth_M_up_all_ctrl.trd_ctrl_vis",0],
    ["nasolabial_M_up_all_ctrl.trd_ctrl_vis",0],
    ["nasolabial_M_up_all_ctrl.sec_ctrl_vis",0],
    ["mouth_M_dn_all_ctrl.sec_ctrl_vis",1],
    ["mouth_M_dn_all_ctrl.naso_ctrl_vis",0],
    ["mouth_M_dn_all_ctrl.trd_ctrl_vis",0],
    ["nasolabial_M_dn_all_ctrl.trd_ctrl_vis",0],
    ["nasolabial_M_dn_all_ctrl.sec_ctrl_vis",0],
    ["face_cheek_L_1_ctrl.nasolabial_L_1_ctrl",0],
    ["face_cheek_R_1_ctrl.nasolabial_R_1_ctrl",0],
    ["face_nostril_L_1_ctrl.sneer",0],
    ["face_nostril_L_1_ctrl.moveScale",0],
    ["face_nostril_L_1_ctrl.flare",0],
    ["face_nostril_R_1_ctrl.sneer",0],
    ["face_nostril_R_1_ctrl.moveScale",0],
    ["face_nostril_R_1_ctrl.flare",0],
    ["eyelid_L_up_all_ctrl.orbita_ctrl_vis",0],
    ["eyelid_R_up_all_ctrl.orbita_ctrl_vis",0],
    ["eyelid_L_up_all_ctrl.sec_ctrl_vis",1],
    ["eyelid_R_up_all_ctrl.sec_ctrl_vis",1],
    ["eyelid_R_dn_all_ctrl.sec_ctrl_vis",1],
    ["eyelid_L_dn_all_ctrl.sec_ctrl_vis",1],
    ["eyelid_R_dn_all_ctrl.orbita_ctrl_vis",0],
    ["eyelid_L_dn_all_ctrl.orbita_ctrl_vis",0],
    ["FKScapula_R_ctrl.Global",0],
    ["FKScapula_L_ctrl.Global",0],
    ["FKIKLeg_R_ctrl.FKIKBlend",10],
    ["FKIKLeg_L_ctrl.FKIKBlend",10],
    ["FKIKArm_R_ctrl.FKIKBlend",0],
    ["FKIKArm_L_ctrl.FKIKBlend",0],
    ["PoleArm_R_ctrl.lock",0],
    ["PoleArm_L_ctrl.lock",0],
    ["PoleArm_R_ctrl.follow",0],
    ["PoleArm_L_ctrl.follow",0],
    ["IKArm_R_ctrl.follow",0.0],
    ["IKArm_R_ctrl.stretchy",0.0],
    ["IKArm_R_ctrl.antiPop",0.0],
    ["IKArm_R_ctrl.Lenght1",1.0],
    ["IKArm_R_ctrl.Lenght2",1.0],
    ["IKArm_R_ctrl.volume",10.0],
    ["IKArm_L_ctrl.follow",0.0],
    ["IKArm_L_ctrl.stretchy",0.0],
    ["IKArm_L_ctrl.antiPop",0.0],
    ["IKArm_L_ctrl.Lenght1",1.0],
    ["IKArm_L_ctrl.Lenght2",1.0],
    ["IKArm_L_ctrl.volume",10.0],
    ["RootX_M_ctrl.legLock",0.0],
    ["RootX_M_ctrl.CenterBtwFeet",0.0],
    ["FKIKSpine_M_ctrl.FKVis",1],
    ["FKIKSpine_M_ctrl.IKVis",1],
    ["IKLeg_R_ctrl.swivel",0.0],
    ["IKLeg_R_ctrl.toe",0.0],
    ["IKLeg_R_ctrl.roll",0.0],
    ["IKLeg_R_ctrl.rollAngle",25.0],
    ["IKLeg_R_ctrl.rock",0.0],
    ["IKLeg_R_ctrl.legAim",0.0],
    ["IKLeg_R_ctrl.stretchy",0.0],
    ["IKLeg_R_ctrl.antiPop",0.0],
    ["IKLeg_R_ctrl.Lenght1",1.0],
    ["IKLeg_R_ctrl.Lenght2",1.0],
    ["IKLeg_R_ctrl.volume",10.0],
    ["IKLeg_L_ctrl.swivel",0.0],
    ["IKLeg_L_ctrl.toe",0.0],
    ["IKLeg_L_ctrl.roll",0.0],
    ["IKLeg_L_ctrl.rollAngle",25.0],
    ["IKLeg_L_ctrl.rock",0.0],
    ["IKLeg_L_ctrl.legAim",0.0],
    ["IKLeg_L_ctrl.stretchy",0.0],
    ["IKLeg_L_ctrl.antiPop",0.0],
    ["IKLeg_L_ctrl.Lenght1",1.0],
    ["IKLeg_L_ctrl.Lenght2",1.0],
    ["IKLeg_L_ctrl.volume",10.0],
    ["PoleLeg_R_ctrl.follow",0.0],
    ["PoleLeg_R_ctrl.lock",0.0],
    ["PoleLeg_L_ctrl.follow",0.0],
    ["PoleLeg_L_ctrl.lock",0.0],

    ["arm_L_wrist_ik_ctrl.follow",0.0],
    ["arm_L_pole_ik_ctrl.follow",0.0],
    ["arm_L_arm_fk_ctrl.follow",0.0],
    ["arm_R_wrist_ik_ctrl.follow",0.0],
    ["arm_R_pole_ik_ctrl.follow",0.0],
    ["arm_R_arm_fk_ctrl.follow",0.0],
    ["head_M_ctrl.follow",0.0],
    ["leg_L_ankle_ik_ctrl.follow",0.0],
    ["leg_L_pole_ik_ctrl.follow",0.0],
    ["leg_L_leg_fk_ctrl.follow",0.0],
    ["leg_R_ankle_ik_ctrl.follow",0.0],
    ["leg_R_pole_ik_ctrl.follow",0.0],
    ["leg_R_leg_fk_ctrl.follow",0.0],
    ["neck_M_1_fk_ctrl.follow",0.0],
    ["spine_M_2_ik_ctrl.position_follow",0],
    ["visibility_ctrl.highlight_box",0],

    ["leg_L_setting_ctrl.ikfk_switch", 1.0],
    ["leg_R_setting_ctrl.ikfk_switch", 1.0],
    ["arm_L_setting_ctrl.ikfk_switch", 0.0],
    ["arm_R_setting_ctrl.ikfk_switch", 0.0],

    ["arm_L_setting_ctrl.finger_vis", 1.0],
    ["arm_R_setting_ctrl.finger_vis", 1.0]
    ] # ["eyeball_M_all_ctrl.eyelidFollow", 3.5],

    for a in attr_list:
        try:
            cmds.setAttr(a[0],int(a[1]))
        except:
            pass

    try:
        if cmds.objExists("visibility_ctrl.char_name"):
            node_name = 'visibility_ctrl'
            attr_name = 'char_name'
            current_value = cmds.getAttr('{}.{}'.format(node_name, attr_name))
            enum_labels = cmds.attributeQuery(attr_name, node=node_name, listEnum=True)[0].split(':')
            current_label = enum_labels[current_value]
            if 'horse' in current_label:
                cmds.setAttr("leg_L_setting_ctrl.ikfk_switch", 1.0)
                cmds.setAttr("leg_R_setting_ctrl.ikfk_switch", 1.0)
                cmds.setAttr("arm_L_setting_ctrl.ikfk_switch", 1.0)
                cmds.setAttr("arm_R_setting_ctrl.ikfk_switch", 1.0)
    except:
        pass

    try:
        if cmds.objExists("global_ctrl.lookPass"):
            lct = cmds.listConnections("global_ctrl.lookPass",s=1,p=1,scn=1) or []
            for a in lct:
                cmds.setAttr(a,0)
            if not lct:
                cmds.setAttr("global_ctrl.lookPass",0)
    except:
        cmds.warning("set global_ctrl.lookPass warning")

    all_mesh = [a.getParent() for a in pm.listRelatives("master",ad=1,type="mesh",ni=1)]
    for mesh in all_mesh:
        mesh.visibility.lock()

    protected = {"defaultLayer", "defaultRenderLayer"}

    for layer_type in ["displayLayer", "renderLayer"]:
        for layer in cmds.ls(type=layer_type) or []:
            if layer in protected:
                continue

            if cmds.referenceQuery(layer, isNodeReferenced=True):
                print("skip referenced layer:", layer)
                continue

            try:
                cmds.delete(layer)
            except:
                pass
            print("already:", layer)

    if cmds.objExists("visibility_ctrl"):
        if cmds.attributeQuery("proxy_vis", node="visibility_ctrl", exists=True):
            try:
                cmds.setAttr("visibility_ctrl.proxy_vis", 1)
            except:
                pass
        else:
            pass

    try:
        if pm.objExists("global_ctrl.scale_offset"):
            pm.setAttr("global_ctrl.scale_offset",l=1)
    except:
        pass

    try:
        all_shapes = pm.listRelatives("poly|hi",type="mesh",ad=1,ni=1)
    except:
        all_shapes = []

    for shape in all_shapes:
        if not shape.hasAttr("origShape"):
            was_locked = bool(pm.lockNode(shape, q=True)[0])
            if was_locked:
                pm.lockNode(shape, l=False)
            shape.addAttr("origShape", dt="string")
            if was_locked:
                pm.lockNode(shape, l=True)
        try:
            shape.attr("origShape").set(";".join(list(set(find_source(shape).l_terminals))))
        except:
            shape.attr("origShape").set(shape)

    try:
        cmds.lockNode('initialShadingGroup', lock=False, lockUnpublished=False)
        cmds.lockNode('renderPartition', lock=False, lockUnpublished=False)
        cmds.lockNode('initialParticleSE', lock=False, lockUnpublished=False)
    except:
        pass
    '''
    follicles = cmds.ls(type = "follicle")
    for a in follicles:
        try:
            cmds.setAttr(a+".simulationMethod",0)
        except:
            pass

    follicles = cmds.ls(type = "hairSystem")
    for a in follicles:
        try:
            cmds.setAttr(a+".simulationMethod",0)
        except:
            pass
    '''

    master = "master"
    bakeattrs = 'master.bakeAttrs'

    if cmds.objExists(master):
        if not cmds.objExists(master+'.bakeAttrs'):
            cmds.addAttr(master,ln='bakeAttrs',m=1,at='message')

    makeRolls = cmds.ls(type = "makeRoll")
    for makeRoll in makeRolls:
        connections = cmds.listConnections(makeRoll+".outRotate",s=0,d=1,scn=1) or []
        if connections:
            try:
                obj = connections[0]
                cmds.lockNode(obj,l=1)
                for attr in ['rx', 'ry', 'rz'] :
                    id = lsUnConnectedAttrId(bakeattrs)
                    print 'connect selected attr : <'+obj+'.'+attr+'>  to  <'+bakeattrs+'['+str(id)+']>'
                    cmds.connectAttr(obj+'.'+attr,bakeattrs+'['+str(id)+']')
            except:
                print traceback.format_exc()
                pass

    for i in cmds.ls("*_ctrl", type="transform"):
        cmds.setAttr("{}.v".format(i), lock=True, channelBox=False, keyable=False)


    # set ["eye_global_loc", "L_eye_loc", "R_eye_loc"] visibility
    loc_array = ["eye_global_loc", "L_eye_loc", "R_eye_loc"]
    for i in loc_array:
        if cmds.objExists(i):
            shape = cmds.listRelatives(i, s=True)[0]
            cmds.setAttr("{}.tx".format(i), lock=True)
            cmds.setAttr("{}.ty".format(i), lock=True)
            cmds.setAttr("{}.tz".format(i), lock=True)
            cmds.setAttr("{}.rx".format(i), lock=True)
            cmds.setAttr("{}.ry".format(i), lock=True)
            cmds.setAttr("{}.rz".format(i), lock=True)
            cmds.setAttr("{}.sx".format(i), lock=True)
            cmds.setAttr("{}.sy".format(i), lock=True)
            cmds.setAttr("{}.sz".format(i), lock=True)
            cmds.setAttr("{}.visibility".format(shape), 0)

    sync_proxy_visibility()

    if cmds.objExists("jaw_M_open_ctrl.fcaePass"):
        cmds.setAttr("jaw_M_open_ctrl.fcaePass", l=1, k=0)

    # if str(proj).lower() == 'xun':
    #     if cmds.objExists("snake_ctrl.path_to_pathCtrl"):
    #         cmds.setAttr("snake_ctrl.path_to_pathCtrl", 0)
    #         cmds.setAttr("snake_ctrl.path_to_pathCtrl", lock=True, channelBox=False, keyable=False)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"统一rig系统的通用控制模式和显示隐藏参数含动力学修改。"
        self.description = u"在设置上传时将一些显示隐藏，跟随，IKFK等参数设置为统一参数！"
        return

    def proceed(self):
        #print self.dialog.project['name'].upper()
        self.dialog.anim_file=self.dialog.version_dir+'/anim_rig/'
        if not self.dialog.project['name'].upper() == 'GOD':
            asset = self.dialog.entity['name']
            proj = self.dialog.project['name']
            try:
                set_defualt_rig_param(proj, asset)
                return ""
            except:
                return traceback.format_exc()
        else:
            return ""


    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description




'''
import maya.cmds as mc
import pymel.all as pm

def getSelectedChannels():
    if not mc.ls(sl=True):
        return
    gChannelBoxName = pm.mel.eval('$temp=$gChannelBoxName')
    sma = mc.channelBox(gChannelBoxName, query=True, sma=True)
    ssa = mc.channelBox(gChannelBoxName, query=True, ssa=True)
    sha = mc.channelBox(gChannelBoxName, query=True, sha=True)

    channels = list()
    if sma:
        channels.extend(sma)
    if ssa:
        channels.extend(ssa)
    if sha:
        channels.extend(sha)

    return channels

sel = mc.ls(sl=1)[0]
attrs = getSelectedChannels()
for attr in attrs:
    print '["%s.%s",%s],'%(sel,attr,mc.getAttr(sel+"."+attr))

'''
