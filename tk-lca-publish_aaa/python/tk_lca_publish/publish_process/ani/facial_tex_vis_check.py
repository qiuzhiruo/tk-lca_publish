# -*- coding:utf-8 -*-
import traceback
import maya.cmds as cmds


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"还原脸部条纹pass默认属性"
        self.description = u"下游不需要脸部条纹pass, 需要还原默认值"
        return


    def chr_is_empty(self, grp_name):
        children = cmds.listRelatives(grp_name,children = True) or []

        if not children:
            return True
        else:
            return False

    def find_ctrl_in_grp(self, grp_name, suffix):

        # 获取组内对象
        grp_obj = cmds.listRelatives(grp_name, ad=True)

        # 遍历组内对象
        matching_ctrl = [ctrl for ctrl in grp_obj if ctrl.endswith(suffix) and cmds.objectType(ctrl) == "transform"]

        return matching_ctrl

    def check_attr(self, ctrl_name, attr_name, default_value):
        full_attr_name = ctrl_name + "." + attr_name
        # 检查该属性是否在控制器上
        if cmds.objExists(full_attr_name):
            # 检查是否为默认值
            current_value = cmds.getAttr(full_attr_name)
            if current_value != default_value:
                cmds.setAttr(full_attr_name, default_value)
                cmds.cutKey(full_attr_name)

    def proceed(self):
        try:
            grp_name = "|assets|chr"
            if not cmds.objExists(grp_name):
                return ""

            suffix = ":visibility_ctrl"
            # 设定检查的属性名和数值
            attr_name = "facial_tex_vis"
            default_value = 0
            if self.chr_is_empty(grp_name):
                return ""
            else:

                ctrl_in_chr_grp = self.find_ctrl_in_grp(grp_name, suffix)
                for ctrl_name in ctrl_in_chr_grp:
                    self.check_attr(ctrl_name, attr_name, default_value)
                return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
