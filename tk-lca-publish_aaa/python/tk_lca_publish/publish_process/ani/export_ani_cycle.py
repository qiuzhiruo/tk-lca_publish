#! -*- coding:utf-8 -*-
import os
import traceback
import maya.cmds as cmds
import ani.lca_cycle_info_tool.poly_reduce_function as prf


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"z33场导出cycle资产ma文件"
        self.description = u"检查场次是不是z33,如果是就导出对应的资产ma文件"
        return

    # def get_ref_namespace(self):
    #     all_ref_asset_master = []
    #     all_ref_names = self.all_refs()
    #     is_loaded = False
    #     for rf in all_ref_names:
    #         try:
    #             is_loaded = cmds.referenceQuery(rf, isLoad=True)
    #         except:
    #             print('=' * 75, '/n', 'This reference node has problem:', rf)
    #             traceback.print_exc()
    #             print('=' * 75, '/n')
    #         if is_loaded:
    #             file_path = cmds.referenceQuery(rf, f=True)
    #             rf_namespace = cmds.referenceQuery(rf, ns=True)
    #             if '/rig/' in file_path:
    #                 if '/chr/' in file_path or '/prp/' in file_path or '/veh/' in file_path:
    #                     current_master = '{}:master'.format(rf_namespace)
    #                     all_ref_asset_master.append(current_master)
    #
    #     return all_ref_asset_master
    #
    #
    # def all_refs(self):
    #     allRefNodes_ = cmds.ls(rf=1)
    #     allRefNodes = []
    #     for ref in allRefNodes_:
    #         try:
    #             cmds.referenceQuery(ref, isLoaded=1)
    #         except:
    #             continue
    #         allRefNodes.append(ref)
    #     return allRefNodes

    def proceed(self):
        try:
            if self.dialog.entity['name'][0:3] != 'z33':
                return ''

            poly_reduce_namespace_list, poly_reduce_file_path, poly_reduce_no_blk_rig = prf.get_poly_reduce_namespace()
            all_ref_master = ['{}:master'.format(i) for i in poly_reduce_namespace_list]
            # all_ref_master = self.get_ref_namespace()
            cmds.select(clear=True)
            for rf in all_ref_master:
                cmds.select(rf, add=True)

            cycle_publish_dir = os.path.join(self.dialog.version_dir, 'extra_data')
            if not os.path.isdir(cycle_publish_dir):
                os.mkdir(cycle_publish_dir)
            cycle_publish_name = 'cycle_{}_srf_rigging.ma'.format(self.dialog.entity['name'])
            cycle_export_file_path = os.path.join(cycle_publish_dir, cycle_publish_name)

            cmds.file(cycle_export_file_path, force=True, options='v=0;', type='mayaAscii', pr=True, exportSelected=True)
        except:
            return traceback.format_exc()
        return ''

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

