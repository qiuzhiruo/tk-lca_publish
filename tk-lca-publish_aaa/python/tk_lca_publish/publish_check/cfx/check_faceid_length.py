# -*-coding:utf-8-*-
"""
 @Time : 7/02/25 10:57 AM
 @Author : baba
"""
import traceback
import maya.cmds as cmds
try:
    import xgenm
    import xgenm.xgGlobal as xgg
except:
    pass


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查羽毛自定义属性的数量和模型的面数是否一致"
        self.description = u"检查羽毛自定义属性的数量和模型的面数是否一致"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return

    def get_patches_from_collection(self, collection_name):
        description_list = cmds.listRelatives(collection_name, c=True)
        desc_patches = xgenm.palettePatches(collection_name)
        if not xgenm.palettes() and not description_list and desc_patches:
            return []

        error_dict = {}
        for desc in desc_patches:
            description_n = [d for d in description_list if desc.endswith(d)]
            if not description_n:
                continue
            mesh = desc.split("_" + description_n[0])[0]
            custom_attr = xgenm.customAttrs(str(collection_name), str(description_n[0]), 'RendermanRenderer')
            if "custom_float_lc_faceid_length" in custom_attr:
                attr_value = xgenm.getAttr("custom_float_lc_faceid_length", str(collection_name), str(description_n[0]), 'RendermanRenderer')
                if not attr_value:
                    attr_value = 0
                mesh_face = cmds.polyEvaluate(mesh, f=True)
                if int(attr_value) == int(mesh_face):
                    continue
                else:
                    error_dict[description_n[0]] = {}
                    error_dict[description_n[0]]['faceid_length'] = attr_value
                    error_dict[description_n[0]]['mesh_face'] = mesh_face
                    # print "{0}   faceid_length:{1}   mesh_face:{2}".format(description_n[0], attr_value, mesh_face)
        if error_dict:
            return error_dict

        return ""

    def run_check(self):
        try:
            error_list = []
            collection_name_list = cmds.ls(type='xgmPalette')
            for collection in collection_name_list:
                return_dict = self.get_patches_from_collection(str(collection))
                if return_dict:
                    error_list.append(return_dict)
            if error_list:
                error_description = []
                for err in error_list:
                    for key, value in err.items():
                        error_description.append(key)
                if error_description:
                    message = "faceid_length Setting Error: " + ", ".join(error_description)
                    return message

            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        collection_name_list = cmds.ls(type='xgmPalette')
        for collection in collection_name_list:
            return_dict = self.get_patches_from_collection(str(collection))
            if not return_dict:
                continue

            for key, value in return_dict.items():
                xgenm.setAttr("custom_float_lc_faceid_length", str(value["mesh_face"]),str(collection), str(key), 'RendermanRenderer')
        de = xgg.DescriptionEditor
        de.refresh('Full')
        return

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty