# -*- coding:utf-8 -*-

import os
import traceback
import pymel.core as pm
import maya.cmds as mc
import math
import shutil

def convertEnumToList(enum_names):
    input_str = str(enum_names)

    if input_str.startswith(u"[u'") and input_str.endswith(u"']"):
        cleaned_str = input_str[3:-2]
        result_list = cleaned_str.split(':')
        return result_list
    else:
        print("Input string format doesn't match expected pattern.")

def ensure_abc_export_loaded():
    """
    Ensure Alembic export plugin is loaded.
    Maya 2019: AbcExport.mll
    """
    plugin_name = "AbcExport"

    if not mc.pluginInfo(plugin_name, q=True, loaded=True):
        try:
            mc.loadPlugin("AbcExport.mll", quiet=True)
            print("Loaded AbcExport plugin.")
        except Exception as e:
            raise RuntimeError(
                "Failed to load AbcExport.mll.\n"
                "Please make sure Alembic is installed.\n{}".format(e)
            )

    return True


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"facePass abc cache"
        self.description = u"facePass abc cache"
        return

    def proceed(self):
        try:
            try:
                self.export_face_pass_abc_cache()

            except:
                print traceback.format_exc()

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description


    def export_face_pass_abc_cache(self):
        facePassAttr = 'visibility_ctrl.facePass'
        enum_names = []
        if mc.objExists(facePassAttr):
            if mc.attributeQuery(facePassAttr.split(".")[1], node=facePassAttr.split(".")[0], exists=True):
                # [u'default:fantasy:c10140:c30020:c90630:c90680:c90700:c90730:gourd']
                enum_names = mc.attributeQuery(facePassAttr.split(".")[1], node=facePassAttr.split(".")[0], listEnum=True)
        else:
            return
        facePass_list = convertEnumToList(enum_names)

        for i, val in enumerate(facePass_list):
            frame = i + 1  # frames start at 1
            print(i, val)
            mc.currentTime(frame)
            mc.setAttr(facePassAttr, i)
            mc.setKeyframe(facePassAttr)
        mc.currentTime(1)

        ensure_abc_export_loaded()
        asset_name = self.dialog.entity['name'].lower()
        version_dir = self.dialog.d_assets_info[asset_name]['version_dir'].lower()
        facePass_abc_file_full_path = "%s/gpu/facePass.abc" % version_dir
        start_frame = '1'
        end_frame = '{}'.format(len(facePass_list))
        top_group = '|master|poly|hi|mesh_grp'
        abc_cmd = '-frameRange {} {} -root {} -file "{}"'.format( start_frame, end_frame, top_group, facePass_abc_file_full_path)

        # Execute Alembic export
        mc.AbcExport(j=abc_cmd)

        facePass_shape_abc_file_full_path = "%s/gpu/facePass_withshape.abc" % version_dir
        if mc.objExists('|master|shape'):
            shape_group = '|master|shape'
            #root_flags = ' '.join(['-root "{}"'.format(grp) for grp in top_groups])
            abc_cmd = '-frameRange {} {} -root {} -file "{}"'.format(start_frame, end_frame, shape_group, facePass_shape_abc_file_full_path)
            mc.AbcExport(j=abc_cmd)
        else:
            abc_cmd = '-frameRange {} {} -root {} -file "{}"'.format(start_frame, end_frame, top_group, facePass_shape_abc_file_full_path)
            mc.AbcExport(j=abc_cmd)

if __name__ == '__main__':
    pass
