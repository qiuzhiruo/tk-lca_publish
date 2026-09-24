# -*- coding:utf-8 -*-

import traceback
import pymel.core as pm
import maya.cmds as cmds
from collections import Counter


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查节点重名。"
        self.description = u"在master组下所有节点的命名是唯一的。\n另外模型和绑定场景内不能有名为 hair, cloth 的 shader，避免影响未来下游CFX的关键组 |master|hair, |master|cloth 命名。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            error_msg = ''
            err_cam = ''
            for key_word in ['persp', 'top', 'front', 'side']:
                l_nodes = pm.ls(key_word)
                if len(l_nodes) > 1:
                    for node in l_nodes:
                        if node.fullPath() not in ['|persp', '|top','|front','|side']:
                            error_msg += u"下面这些节点名字为在['persp', 'top', 'front', 'side']内,它会影响未来 RIG 的节点命名。请删除或重命名后再 publish。\n"

            err_cfx_list = []
            same_name_info = {}
            err_same_name = u"下面这些节点出现重名:\n"
            for asset_name in self.dialog.d_assets_info.keys():
                for node in pm.listRelatives(asset_name, ad=True):
                    if node.name() in ['hair', 'cloth']:
                        err_cfx_list.append(node.fullPath())

                l_res = ['hi', 'md', 'lo', 'proxy', 'misc']

                d_name = {}
                for res_str in l_res:
                    for lod_node in pm.listRelatives(asset_name, ad=True):
                        if lod_node.name().split('|')[-1] == res_str:
                            res = lod_node
                            node_list = pm.listRelatives(res, ad=True, fullPath=True)
                            if pm.objExists('|{}|shape'.format(asset_name)):
                                node_list.extend(pm.listRelatives('|{}|shape'.format(asset_name), ad=True, fullPath=True))
                            for node in node_list:
                                node_name = res.fullPath() + ': ' + node.name().split('|')[-1]
                                if node_name not in d_name:
                                    d_name[node_name] = []
                                full_path_list = []
                                if not node_name.endswith('mesh_grp'):
                                    full_path_list.append(node.fullPath())
                                d_name[node_name] += list(set(full_path_list))

                            for name, l_paths in d_name.items():
                                if len(l_paths) > 1:
                                    err_same_name += u'{}\n'.format('\n'.join(l_paths))
                                    same_name_info.update({asset_name: {name: l_paths}})
                                    print err_same_name
                if same_name_info:
                    same_name_info.update({asset_name: d_name})
            if err_cfx_list:
                error_msg += u'下面这些节点名字为 hair或cloth. 它会影响未来 CFX 的节点命名。请删除或重命名后再 publish。\n{}\n'.format('\n'.join(err_cfx_list))

            if same_name_info:
                error_msg += err_same_name

            return error_msg

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        return ''

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


