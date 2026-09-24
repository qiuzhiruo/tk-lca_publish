# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Create a version on shotgun
#
############################################

import os
import sys
import traceback
import pprint
import string
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun上建立版本并链接到任务"
        self.description = u"在shotgun上建立版本并链接到任务"
        return


    def proceed(self):
        try:
            if sys.platform.startswith('win'):
                local_path = self.dialog.version_dir.replace('/', '\\') + '\\'
            else:
                local_path = self.dialog.version_dir + '/'

            if not hasattr(self.dialog, 'auto_pub') or not self.dialog.auto_pub:
                desc_txt = self.dialog.w_publish.plainTextEdit_auto_description.toPlainText()
                if desc_txt != '':
                    if desc_txt.__class__.__name__ == 'QString':
                        desc_txt = str(desc_txt.toUtf8())
                    elif desc_txt.__class__.__name__ == 'str':
                        desc_txt=desc_txt.decode('utf-8')
                    self.dialog.description += '  \n { ' + desc_txt + ' }'

            if self.dialog.task['name'] != 'animation':
                d_v_type = {0:'Daily', 1:'Downstream'}
            else:
                d_v_type = {0:'Daily', 1:'Checked', 2:'Downstream'}
            
            if self.dialog.step['name'] == 'ani' and self.dialog.entity_type == 'Shot' and self.dialog.task['name'] == 'animation' and self.dialog.ui.comboBox_publish_mode.currentIndex()>=1:
                shotPassStr = u'镜头-角色-Pass 信息:\n{\n'
                shot_name = self.dialog.entity['name']
                shot_cam = shot_name+'_cam'
                import maya.cmds as cmds

                # 此处不再直接获取相机的 lca_shot_chr_pass 属性值
                # 考虑到检查项会修复相机，变成ref状态，会导致 lca_shot_chr_pass 属性丢失，或者属性值不是当前文件的最新数据（因为ref的是pub出去的相机，记录的是当时的数据
                # 在整个 publish 页面，进入到 publish process 的时候，获取 dailog 曾经赋予的 shot_pass_dict 值，此属性值的数据为 最新所有角色的 pass 信息

                # shot_pass_dict = eval(cmds.getAttr(shot_cam+'.lca_shot_chr_pass'))

                shot_pass_dict = self.dialog.shot_pass_dict
                # 这里再次判定 相机是否 有 lca_shot_chr_pass 属性，没有就添加上去，方便写出 shot pass json 数据时直接获取
                # 解锁相机，为了增加属性
                cmds.select(shot_cam)
                import pymel.core as pm
                tops = pm.ls(sl = True)
                for top in tops:
                    all = pm.listRelatives(top, allDescendents = True)
                    all.append(top)
                    for c in all:
                        pm.lockNode(c, lock = False)
                shot_allAttrs = cmds.listAttr(shot_cam)
                shot_pass_attr = 'lca_shot_chr_pass'
                if shot_pass_attr not in shot_allAttrs:
                    cmds.addAttr(shot_cam, ln=shot_pass_attr, dt='string')
                cmds.setAttr(shot_cam+'.'+shot_pass_attr,str(shot_pass_dict),type='string')

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
                self.dialog.description += ' \n'+shotPassStr
            
            if self.dialog.step['name'] == 'flo' and self.dialog.entity_type == 'Shot' and self.dialog.task['name'] == 'final_layout' and self.dialog.ui.comboBox_publish_mode.currentIndex()==1:
                shotPassStr = u'镜头-角色-Pass 信息:\n{\n'
                shot_name = self.dialog.entity['name']
                shot_cam = shot_name+'_cam'
                import maya.cmds as cmds

                # 此处不再直接获取相机的 lca_shot_chr_pass 属性值
                # 考虑到检查项会修复相机，变成ref状态，会导致 lca_shot_chr_pass 属性丢失，或者属性值不是当前文件的最新数据（因为ref的是pub出去的相机，记录的是当时的数据
                # 在整个 publish 页面，进入到 publish process 的时候，获取 dailog 曾经赋予的 shot_pass_dict 值，此属性值的数据为 最新所有角色的 pass 信息

                # shot_pass_dict = eval(cmds.getAttr(shot_cam+'.lca_shot_chr_pass'))

                shot_pass_dict = self.dialog.shot_pass_dict
                # 这里再次判定 相机是否 有 lca_shot_chr_pass 属性，没有就添加上去，方便写出 shot pass json 数据时直接获取
                # 解锁相机，为了增加属性
                cmds.select(shot_cam)
                import pymel.core as pm
                tops = pm.ls(sl = True)
                for top in tops:
                    all = pm.listRelatives(top, allDescendents = True)
                    all.append(top)
                    for c in all:
                        pm.lockNode(c, lock = False)
                shot_allAttrs = cmds.listAttr(shot_cam)
                shot_pass_attr = 'lca_shot_chr_pass'
                if shot_pass_attr not in shot_allAttrs:
                    cmds.addAttr(shot_cam, ln=shot_pass_attr, dt='string')
                cmds.setAttr(shot_cam+'.'+shot_pass_attr,str(shot_pass_dict),type='string')

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
                self.dialog.description += ' \n'+shotPassStr
            
            d_version = {'project':self.dialog.project, 'entity':self.dialog.entity, \
                        'sg_task':self.dialog.task,'code':self.dialog.version_name, \
                        'description':self.dialog.description, 'user':self.dialog.user, \
                        'sg_version_folder':{ 'local_path': local_path, 'name':self.dialog.version_name, \
                        'content_type':None, 'link_type':'local'} , \
                        'sg_version_type': d_v_type[self.dialog.publish_mode], \
                        'tag_list':[self.dialog.version_tag], 'created_by':self.dialog.user}
            d_version_str = self.__dict_qstr2str(d_version)
            print 'd_version_str\n', d_version_str
            v_info = self.dialog.sg.create('Version', d_version_str)
            if not v_info:
                return  pprint.pformat(d_version_str)

            self.dialog.v_info = v_info

            # Set related tasks
            task_info = self.dialog.sg.find_one('Task', [['id', 'is', self.dialog.task['id']]], ['step'])
            l_tasks = self.dialog.sg.find('Task', [['entity', 'is', self.dialog.entity]], ['step'])
            l_related_tasks = [task_info]

            #print 'local_path : '+local_path
            print d_version
            #print d_version_str
            #print v_info
            #print task_info
            #print l_tasks
            #print l_related_tasks

            for task in l_tasks:
                if self.dialog.entity['type'] == 'Asset' and task_info['step']['name'] == 'art':
                    if task['step']['name'] == 'mod':
                        l_related_tasks.append(task)
                elif self.dialog.entity['type'] == 'Asset' and task_info['step']['name'] == 'mod':
                    if not task['step']['name'] in ['art', 'mod']:
                        l_related_tasks.append(task)
                elif self.dialog.entity['type'] == 'Shot' and task_info['step']['name'] == 'lay':
                    if task['step']['name'] != 'lay':
                        l_related_tasks.append(task)

            self.dialog.sg.update('Version', self.dialog.v_info['id'], {'sg_related_tasks': l_related_tasks })

            # Link to the 'last version' field of task
            self.dialog.sg.update('Task', self.dialog.task['id'], {'sg_last_version': v_info})
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

