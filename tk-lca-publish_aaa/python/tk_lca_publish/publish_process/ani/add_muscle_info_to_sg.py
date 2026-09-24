#! -*- coding:utf-8 -*-
import os
import shutil
import traceback
import pymel.core as pm
import maya.cmds as cmds
import json
from production import shotgun_connection
# All publish process will use StdProcess as the class name.
import json
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun镜头页面添加肌肉信息"
        self.description = u"如果镜头文件中打开了肌肉效果,则在shotgun的Muscle Assets Info字段上标注"

        self.proj = self.dialog.project['name'].lower()
        self.shot = self.dialog.entity['name']
        self.muscle_field_name = 'sg_muscle_assets_info'
        self.sg = shotgun_connection.Connection('get_shot_info').get_sg()
        return

    def get_muscle_list_from_shotgun(self):
        muscle_info_list = self.sg.find_one('Shot',
                                            [['project', 'name_is', self.proj.upper()],
                                             ['code', 'is', self.shot]],
                                            [self.muscle_field_name])
        if muscle_info_list:
            muscle_info = muscle_info_list[self.muscle_field_name]
            return muscle_info

    def get_muscle_info_from_file(self):
        muscle_helper = BoneDynamicsNodeHelper()
        ref_node_namespace_list = muscle_helper.get_all_references_with_namespace() #list[str]
        if not ref_node_namespace_list:
            return
        muscle_info = muscle_helper.check_bone_dynamics_nodes(ref_node_namespace_list) #type:list[dict]
        return muscle_info

    def add_tag_for_rra_shot(self):
        shotEntity = self.sg.find_one('Shot', [['project', 'name_is', self.proj],
                                                      ['code', 'is', self.shot]], ['id'])
        muscle_info_list = self.get_muscle_info_from_file()
        str_muscle_info = json.dumps(muscle_info_list, indent=2, ensure_ascii=False)
        muscle_sg_info = self.get_muscle_list_from_shotgun()
        if not str_muscle_info:
            return
        #[NOTE]:如果sg标记的信息和文件中相同则不再更新
        if str_muscle_info != 'null' and muscle_sg_info != str_muscle_info:
            self.sg.update('Shot', shotEntity['id'], {self.muscle_field_name: str_muscle_info})
            print('[INFO] Add %s : %s for %s' % (self.muscle_field_name, str_muscle_info,self.shot))
            
        elif muscle_sg_info == str_muscle_info:
            print('[INFO]: Already add sg_muscle_assets_info , skip......')
        else:
            print('[INFO]: NO MUSCLE')

    def proceed(self):
        try:
            self.add_tag_for_rra_shot()
            return ""
        except:
            return traceback.format_exc()
    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
    
class BoneDynamicsNodeHelper(object):
    
    def __init__(self):
        self.muscle_info_list = [] #type:list[dict]
    @staticmethod
    def get_all_references_with_namespace():
        all_refs = cmds.ls(type='reference')
        user_refs = []
        for ref in all_refs:
            try:
                if not cmds.referenceQuery(ref, isLoaded=True):
                    continue
                namespace = cmds.referenceQuery(ref, namespace=True, shortName=True)
                file_path = cmds.referenceQuery(ref, filename=True)
                if 'chr' not in file_path:
                    print("Skip ! Not a chr asset: [{}]".format(namespace))
                    continue
                user_refs.append(namespace)
                print("the user_refs,",user_refs)
            except RuntimeError as e:
                print("{} id error:{}".format(ref,e))
                continue
           
        print("user_refs",user_refs)
        return user_refs
    
    '''获取相关角色boneDynamicsNode节点控制器的开关,若属性打开则需要写信息到sg'''
    def check_bone_dynamics_nodes(self,namespace_list):
        if not namespace_list:
            return
        for namespace in namespace_list:
            ctrl_name = namespace+':mus_dynamic_ctrl.'
            muscle_ctrl_attr_pri = ctrl_name+'enable_pri'
            muscle_ctrl_attr_sec = ctrl_name+'enable_sec'
            for attr in [muscle_ctrl_attr_pri,muscle_ctrl_attr_sec]:
                if cmds.objExists(attr) and cmds.getAttr(attr) == 1:
                    start_frame = cmds.getAttr(ctrl_name+'start_frame')
                    fps = cmds.getAttr(ctrl_name+'fps')
                    print("[{}]肌肉效果打开了".format(namespace))
                    self.muscle_info_list.append({
                            'namespace': namespace if namespace else "None",
                            'start_frame': start_frame,
                            'fps':fps
                        })
                    break
                else:
                    print("[{}]肌肉效果未打开或不存在".format(namespace))
                    break
        if self.muscle_info_list:
            return self.muscle_info_list