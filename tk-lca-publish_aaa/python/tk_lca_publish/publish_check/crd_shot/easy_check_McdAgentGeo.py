# -*- coding: utf-8 -*-
# @Time    : 18-8-8 下午3:44
# @Author  : zhangzheng
__author__ = 'zhangzheng'
__maintainer__ = 'zhangzheng'

import traceback
import pymel.core as pm

# def compared_mesh_path():
#     agents = pm.ls(type='McdAgentGroup')
#     oat_comp_dict = {}
#     oat_keeps = [i.listRelatives(c=1)[0] for j in agents for i in j.listRelatives(c=1) if
#                  ':Geometry_' in i.name()]
#
#     for oat in oat_keeps:
#         oats = pm.listRelatives(oat, ad=1)
#         oats.append(oat)
#         oat_ns = oat.namespace()
#         oat_key = oat.name().replace(oat_ns, '')
#         oat_rp = '|'.join(oat.fullPath().replace(oat_ns, '').split('|')[:4])
#         oat_c = [i.fullPath().replace(oat_ns, '').replace(oat_rp, '') for i in oats]
#         oat_comp_dict[oat_key] = oat_c
#
#
#     error_agent = []
#     mcdAgentGeos = pm.ls('McdAgentGeometry_*', type='transform')
#     for agent in mcdAgentGeos:
#         check_keep = agent.listRelatives(c=1)[0]
#         check_rp = '|' + check_keep.fullPath().split('|')[1]
#         check_c = [i.fullPath().replace(check_rp, '') for i in agent.listRelatives(ad=1)]
#         check_oat = check_keep.name().split('|')[1]
#         if check_oat in oat_comp_dict.keys():
#             if len([i for i in check_c if i not in oat_comp_dict[check_oat]]) != 0:
#                 error_agent.append(agent.name())
#         else:
#             error_agent.append(agent.name())
#
#     if len(error_agent) == 0:
#         return ''
#     else:
#         return error_agent


    
# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查Agent"
        self.description = u"文件内要有实例好的群集模型，用来出cache。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def compar_sgotgun_asset(self):
        err_msg = []
        agents = pm.ls(type='McdAgentGroup')
        for agent in agents:
            agent_name = agent.split('|')[-1].replace('Agent_','')
            shotgun_asset = self.dialog.sg.find_one('Asset',[['project','is',self.dialog.project],['code','is',agent_name]],['code'])
            if not shotgun_asset:
                err_msg.append(agent.name())
        if len(err_msg) == 0:
            return ''
        else:
            return err_msg

    def run_check(self):
        try:
            if self.dialog.publish_mode == 0:
                return ''
            mcdAgentGeos = pm.ls('McdAgentGeometry_*', type='transform')
            if len(mcdAgentGeos) == 0:
                return u'场景中没有实例好的群集模型，请保持层级实例模型\n'
            else:
                miarmyContent = pm.ls('Miarmy_Contents')
                if len(miarmyContent) == 0:
                    return u'场景中没有唯一的Miarmy_Contents节点，请检查\n'
                else:
                    errors = self.compar_sgotgun_asset()
                    if errors == '':
                        return ''
                    else:
                        return u'以下Agent没有对应shotgun资产，请检查\n\t %s '%'\n\t'.join(errors)

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

