# -*- coding: utf-8 -*-

import maya.cmds as cmds
import traceback
import maya.OpenMaya as om

import gene.scene_data_record.pass_attr_locker as pal

reload(pal)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"对角色的pass控制器属性进行锁定"
        self.description = u"shot环节没有特殊要求，制作人员不能修改pass数值"

        self.seq_allow_skip = ('z55', 'z88', 'z99')
        return

    # def pass_ctrl_empty(self):
    #     # 定义搜索字符串
    #     search_ctrl = ("weaponry_ctrl", "cloth_vis_ctrl", "visibility_ctrl")
    #
    #     # 获取所有 transform 节点
    #     all_trans = cmds.ls(type='transform')
    #
    #     pass_ctrl = [trans for trans in all_trans if trans.endswith(search_ctrl)] or []
    #
    #     if not pass_ctrl:
    #         return  True
    #     else:
    #         return False
    #
    # def find_pass_ctrl(self):
    #     """
    #     遍历场景中的所有 transform 节点，找出名称为 "weaponry_ctrl" 或 "cloth_vis_ctrl" 的控制器。
    #
    #     Returns:
    #         list: 包含符合条件的控制器名称的列表。
    #     """
    #     # 定义搜索字符串
    #     search_strings = ("weaponry_ctrl", "cloth_vis_ctrl", "visibility_ctrl")
    #
    #     # 获取所有 transform 节点
    #     all_transforms = cmds.ls(type='transform')
    #
    #     # 使用列表推导式过滤符合条件的控制器
    #     result = [transform for transform in all_transforms if transform.endswith(search_strings)]
    #
    #     return result
    #
    # def lock_attribute_on_reference_node(self,node_name, attribute_name):
    #     """
    #     锁定reference状态的节点上的指定属性。
    #
    #     :param node_name: reference节点的名称（例如 'myRefRN'）
    #     :param attribute_name: 要锁定的属性名称（例如 'translateX'）
    #     """
    #     # 获取节点的MObject
    #     sel_list = om.MSelectionList()
    #     sel_list.add(node_name)
    #     node_obj = om.MObject()
    #     sel_list.getDependNode(0, node_obj)
    #
    #     # 获取属性的MPlug
    #     fn_node = om.MFnDependencyNode(node_obj)
    #     attr_plug = fn_node.findPlug(attribute_name)
    #
    #     # 锁定属性
    #     attr_plug.setLocked(True)
    #
    #     # 修正打印语句
    #     print(u"属性 {}.{} 已被锁定。".format(node_name, attribute_name))

    def proceed(self):
        try:
            if self.dialog.entity['name'][:3] in self.seq_allow_skip:
                print('[INFO]: {} allow skip pass lock!'.format(str(self.seq_allow_skip)))
                return ""

            pal_obj = pal.PassAttrLocker()
            controllers = pal_obj.find_pass_ctrl()
            if not controllers:
                return ""

            print(u"找到的控制器：{}".format(controllers))

            start_frame = cmds.playbackOptions(q=True, min=True)
            cmds.setKeyframe(controllers, time=start_frame)

            ctrl_attrs = pal_obj.find_vis_attrs()
            for controller in ctrl_attrs.keys():
                attributes = ctrl_attrs.get(controller, [])
                for attr in attributes:  # 遍历每个属性
                    pal_obj.set_ref_attr_lock_status(controller, attr, lock=True)

            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
