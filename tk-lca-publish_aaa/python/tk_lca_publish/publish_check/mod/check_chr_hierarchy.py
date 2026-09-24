# -*- coding:utf-8 -*-
import pymel.core as pm
import traceback
from proc.function_running_time import record_time


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查角色资产模型层级结构。"
        self.description = u"用于检查rws的角色模型层级结构（tag:'skip_name_check'）\n" \
                           u"应有|master|poly|hi|mesh_grp|skin_grp层级，其中应至少包含body_geo,eyeelse_baffle_plate、mouth_grp（mouth_grp中应有且仅有gums_geo、ongue_geo、" \
                           u"teeth_up_geo、teeth_down_geo四种物体）、lacrimal_gland_a、lacrimal_gland_b、nail、L_eyeball_geo_grp与R_eyeball_geo_grp。" \
                           u"并应有|master|shape层级，其中应至少包含eyelash_up、hair_grp、eyebrows、head_geo与head_eyes_open_geo。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        """
        check function
        @return: 
        """
        try:
            # check if low model:
            if self.dialog.version_tag == u"粗模":
                return ''
            # check if rws:
            if self.dialog.project['name'].upper() != 'RWS':
                return ''
            # check if chr:
            asset_type_list = [self.dialog.d_assets_info[key]['type'] for key in self.dialog.d_assets_info.keys()]
            for asset_name in self.dialog.d_assets_info.keys():
                sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
                if 'skip_name_check' in sg_info['tag_list']:
                    print "skip rws_chr_check_hierarchy"
                    return ''
                asset_type = self.dialog.d_assets_info[asset_name]['type']
                if asset_type in ['chr'] and 'asm' not in asset_type_list:
                    # check skin_grp:
                    if not pm.objExists("|master|poly|hi|mesh_grp|skin_grp"):
                        return u"没有找到|master|poly|hi|mesh_grp|skin_grp层级。"
                    skin_grp_res = pm.listRelatives("|master|poly|hi|mesh_grp|skin_grp", c=True)
                    skin_grp_content = [res.nodeName() for res in skin_grp_res]
                    skin_grp_needs_content = ['mouth_grp','eyeelse_baffle_plate',
                                      'lacrimal_gland_a','lacrimal_gland_b','nail',
                                      'L_eyeball_geo_grp','R_eyeball_geo_grp','body_geo']
                    for needs_content in skin_grp_needs_content:
                        if needs_content not in skin_grp_content:
                            return u"|master|poly|hi|mesh_grp|skin_grp层级下没有"+needs_content

                    # check mouth_grp:
                    mouth_grp_res = pm.listRelatives("|master|poly|hi|mesh_grp|skin_grp|mouth_grp", c=True)
                    mouth_grp_content = [res.nodeName() for res in mouth_grp_res]
                    mouth_grp_needs_content = ['gums_geo', 'tongue_geo', 'teeth_up_geo', 'teeth_down_geo']
                    if sorted(mouth_grp_content) != sorted(mouth_grp_needs_content):
                        return u"|master|poly|hi|mesh_grp|skin_grp|mouth_grp层级下应有且仅有gums_geo,tongue_geo,teeth_up_geo,teeth_down_geo。"

                    # check shape:
                    if not pm.objExists("|master|shape"):
                        return u"没有找到|master|shape层级。"
                    shape_content = self._get_all_children("|master|shape")
                    # print shape_content
                    shape_needs_content = ['eyelash_up','hair_grp','eyebrows','head_geo','head_eyes_open_geo']
                    if 'monk' in sg_info['tag_list']:
                        shape_needs_content = ['eyelash_up', 'eyebrows', 'head_geo', 'head_eyes_open_geo']
                    for shape_needs in shape_needs_content:
                        if shape_needs not in shape_content:
                            return u"|master|shape层级必须包含eyelash_up、hair_grp、eyebrows、head_geo、head_eyes_open_geo,现缺少"+shape_needs
            return ""

        except:
            return traceback.format_exc()

    def _get_all_children(self,parent_path):
        children_lst = []
        def dfs(parent_path):
            res_list = pm.listRelatives(parent_path, c=True)
            if res_list:
                for res in res_list:
                    children_lst.append(res.nodeName())
                for res in res_list:
                    dfs(res.fullPath())
        dfs(parent_path)
        return children_lst

    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info

    def run_fix(self):
        '''Auto Fix'''
        return

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
