# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.06
#
# Description: Create versions on shotgun
#
############################################

import os
import sys
import traceback
import pprint
import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds
import string
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun上建立版本"
        self.description = u"在shotgun上建立版本。"
        return


    def proceed(self):
        try:
            if sys.platform.startswith('win'):
                local_path =  self.dialog.version_dir.replace('/', '\\') + '\\'
            else:
                local_path = self.dialog.version_dir + '/'

            desc_shot_msg = ''
            i = 1
            for shot_info in self.dialog.shots_preview_data:
                shot_name = shot_info['shot_info']['code']
                desc_shot_msg += shot_name + '/'
                if i != 1 and i % 5 == 0:
                    desc_shot_msg += '\n'
                i += 1

            ############################################ 获取镜头内每个ref角色的 pass 信息，用于修改描述
            # chrPassDict = {}
            
            # allRefNodes = self.all_refs()
            # for refNode in allRefNodes:
            #     if cmds.referenceQuery(refNode,il=1):
            #         refNodeName = cmds.referenceQuery(refNode,rfn=1)
            #         refNodeFile = cmds.referenceQuery(refNode,f=1)
            #         refNodeNamespace = cmds.referenceQuery(refNode,ns=1)
            #         if '/asset/chr/' in refNodeFile:
            #             visib_Ctrl = refNodeNamespace[1:]+':visibility_ctrl'

            #             allAttrs = cmds.listAttr(visib_Ctrl)
            #             lca_pass_attr = [i for i in allAttrs if 'lca_lookPass_' in i or 'lca_rigPass_' in i]
            #             chrPassDict[refNodeNamespace]={}
            #             for pass_attr in lca_pass_attr:
            #                 chrPassDict[refNodeNamespace][pass_attr]=cmds.getAttr(visib_Ctrl+'.'+pass_attr)

            # chrPassStr = u'镜头-角色-Pass 信息:\n{'
            # for chr_key in chrPassDict.keys():
            #     chr_key_nsp = chr_key[1:]
            #     chrPassStr = chrPassStr+chr_key_nsp+'\n'
            #     for passName_key in chrPassDict[chr_key].keys():
            #         shot_name = passName_key.split('_')[-1]
            #         pass_name = passName_key.split('_')[-2]
            #         chrPassStr = chrPassStr+shot_name+' '+pass_name+(u' : %s' % chrPassDict[chr_key][passName_key])+'\n'
            # chrPassStr = chrPassStr+'}'

            shotPassStr = u'镜头-角色-Pass 信息:\n{\n'

            if self.dialog.step['name'] == 'lay' and self.dialog.ui.comboBox_publish_mode.currentIndex()==1:

                for data in self.dialog.shots_preview_data:
                    shot_name = data['shot_info']['code']

                    shot_cam = shot_name+'_cam'
                    shot_pass_dict = eval(cmds.getAttr(shot_cam+'.lca_shot_chr_pass'))
                    if len(shot_pass_dict.keys())>0:
                        shotPassStr = shotPassStr+shot_name+'\n'

                        
                        for chr_key in shot_pass_dict.keys():
                            shot_asset_nsp = chr_key.rstrip(string.digits)
                            # 判定，只有1级,2级角色才符合，并且勾选 sg_is_reference_one_time
                            aseet_difficulty = self.dialog.sg.find_one("Asset",[['project', 'is', self.dialog.project],
                                                                                ['code', 'is', shot_asset_nsp]],['sg_diffculty2','sg_is_reference_one_time','sg_asset_type'])
                            if aseet_difficulty:
                                if aseet_difficulty['sg_asset_type']=='chr':
                                    if aseet_difficulty['sg_diffculty2']=='1' or aseet_difficulty['sg_diffculty2']=='2':
                                        if aseet_difficulty['sg_is_reference_one_time']:

                                            shotPassStr = shotPassStr+chr_key+' { '

                                            for passName_key in shot_pass_dict[chr_key].keys():
                                                
                                                shotPassStr = shotPassStr+passName_key+':'+shot_pass_dict[chr_key][passName_key]+', '
                                            shotPassStr = shotPassStr[:-2]+' }'+'\n'
            shotPassStr = shotPassStr+'}'

            ############################################
            d_v_type = {0:'Daily', 1:'Downstream'}
            d_version = {'project':self.dialog.project,
                         'entity':self.dialog.entity,
                         'sg_task':self.dialog.task,
                         'code':self.dialog.version_name,
                         'description':self.dialog.description +
                                       u' \n(from ' + self.dialog.version_name + u', including:\n%s)' % desc_shot_msg+'\n'+shotPassStr,
                         'sg_remark':self.dialog.version_name, 
                         'user':self.dialog.user,
                         'sg_version_folder':{'local_path':local_path,
                                              'name':self.dialog.version_name,
                                              'link_type':'local'} ,
                         'sg_version_type':d_v_type[self.dialog.publish_mode],
                         'tag_list':[self.dialog.version_tag],
                         'created_by':self.dialog.user}
            d_version_str = self.__dict_qstr2str(d_version)

            self.dialog.v_info = self.dialog.sg.create('Version', d_version_str)
            if not self.dialog.v_info:
                return  pprint.pformat(d_version_str)
            ############################################ seq rough lay 版本描述里写的是全部镜头的全部角色的pass信息，shot rough lay 版本描述里写的是单个镜头的全部角色的pass信息
            # for data in self.dialog.shots_preview_data:
            #     # print 
            #     # print '>>>>>>>>>>>>>>>>>>data',data
            #     # print 'd_version_str',d_version_str
            #     # print 
            #     shot_name = data['shot_info']['code']
            #     shot_description_dict = chrPassDict
            #     # print 
            #     # print 'shot_name >>',shot_name
            #     # print 'shot_description_dict >>',shot_description_dict
            #     # print 
            #     new_shot_description_dict = {}
            #     # print 
            #     # print 'new_shot_description_dict >>',new_shot_description_dict
            #     # print
            #     for refNodeNamespace in shot_description_dict.keys():
            #         new_shot_description_dict[refNodeNamespace]={}
            #         for pass_attr in shot_description_dict[refNodeNamespace].keys():
            #             if shot_name in pass_attr:
            #                 new_shot_description_dict[refNodeNamespace][pass_attr]=shot_description_dict[refNodeNamespace][pass_attr]
            #     # print 
            #     # print 'new_shot_description_dict >>',new_shot_description_dict
            #     # print
            #     chrPassStr = u'%s-角色-Pass 信息:\n{' % shot_name
            #     for chr_key in new_shot_description_dict.keys():
            #         chr_key_nsp = chr_key[1:]
            #         chrPassStr = chrPassStr+chr_key_nsp+'\n'
            #         for passName_key in new_shot_description_dict[chr_key].keys():
            #             shot_name = passName_key.split('_')[-1]
            #             pass_name = passName_key.split('_')[-2]
            #             chrPassStr = chrPassStr+shot_name+' '+pass_name+(u' : %s' % new_shot_description_dict[chr_key][passName_key])+'\n'
            #     chrPassStr = chrPassStr+'}'
            #     shot_description = self.dialog.description + u' \n(from ' + self.dialog.version_name + u', including:\n%s)' % desc_shot_msg+'\n'+chrPassStr
            #     # print 
            #     # print 'chrPassStr >>',chrPassStr
            #     # print
            
            
            for data in self.dialog.shots_preview_data:

                shot_PassStr = u'镜头-角色-Pass 信息:\n{\n'
                if self.dialog.step['name'] == 'lay' and self.dialog.ui.comboBox_publish_mode.currentIndex()==1:
                    shot_name = data['shot_info']['code']

                    shot_cam = shot_name+'_cam'
                    shot_pass_dict = eval(cmds.getAttr(shot_cam+'.lca_shot_chr_pass'))
                    if len(shot_pass_dict.keys())>0:
                        shot_PassStr = shot_PassStr+shot_name+'\n'

                        
                        for chr_key in shot_pass_dict.keys():
                            shot_asset_nsp = chr_key.rstrip(string.digits)
                            # 判定，只有1级,2级角色才符合，并且勾选 sg_is_reference_one_time
                            aseet_difficulty = self.dialog.sg.find_one("Asset",[['project', 'is', self.dialog.project],
                                                                                ['code', 'is', shot_asset_nsp]],['sg_diffculty2','sg_is_reference_one_time','sg_asset_type'])
                            if aseet_difficulty:
                                if aseet_difficulty['sg_asset_type']=='chr':
                                    if aseet_difficulty['sg_diffculty2']=='1' or aseet_difficulty['sg_diffculty2']=='2':
                                        if aseet_difficulty['sg_is_reference_one_time']:
                                            shot_PassStr = shot_PassStr+chr_key+' { '

                                            for passName_key in shot_pass_dict[chr_key].keys():
                                                
                                                shot_PassStr = shot_PassStr+passName_key+':'+shot_pass_dict[chr_key][passName_key]+', '
                                            shot_PassStr = shot_PassStr[:-2]+' }'+'\n'
                shot_PassStr = shot_PassStr+'}'
                shot_description = self.dialog.description + u' \n(from ' + self.dialog.version_name + u', including:\n%s)' % desc_shot_msg+'\n'+shot_PassStr
                ############################################ 
                task = self.dialog.sg.find_one('Task',
                                               [['entity', 'is', data['shot_info']],
                                                ['step', 'name_is', 'lay'], ['content', 'is', 'rough_layout']],
                                               ['task_assignees'])
                local_path = data['version_dir'] + os.path.sep
                d_version_str.update(entity=data['shot_info'],
                                     sg_task=task,
                                     code=data['version_name'],
                                     sg_version_folder={'local_path':local_path,
                                                        'name':data['version_name'],
                                                        'link_type':'local'},
                                    description=shot_description)

                # if DS and shot rough_layout task has no "Assign to", fill the blank with current user.
                data['task_info'] = task
                if not task['task_assignees'] and self.dialog.publish_mode == 1:
                    self.dialog.sg.update('Task', data['task_info']['id'], {'task_assignees': [self.dialog.user]})

                # create shot rough_layout version
                data['version_info'] = self.dialog.sg.create('Version', d_version_str)
                tasks = self.dialog.sg.find('Task', [['entity', 'is', data['shot_info']]])
                self.dialog.sg.update('Version', data['version_info']['id'], {'sg_related_tasks':tasks})

            return ""

        except:
            return traceback.format_exc()

    def __dict_qstr2str(self,dict_data):
        result={}
        for k,v in dict_data.items():
            if v.__class__.__name__ == 'QString':
                result[k]=unicode(v)
            elif v.__class__.__name__ == 'list':
                new_v=[]
                for vv in v:
                    if vv.__class__.__name__ == 'QString':
                        new_v.append(unicode(vv))
                    else:
                        new_v.append(vv)
                result[k]=new_v
            else:
                result[k]=v
        return result

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

    def all_refs(self):
        allRefNodes_ = cmds.ls(rf=1)
        allRefNodes = []
        for ref in allRefNodes_:
            try:
                cmds.referenceQuery(ref, isLoaded=1)
                if not cmds.referenceQuery(ref, filename=1):
                    continue
            except:
                continue
            allRefNodes.append(ref)
        return allRefNodes