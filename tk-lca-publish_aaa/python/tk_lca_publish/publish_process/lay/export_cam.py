# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Proceed layout publish files
#
############################################

import os, re
import sys
import traceback
import shutil

import pymel.core as pm
import maya.mel as mel

import lay.exportCamera.exportAbcCamera as expCam

reload(expCam)

import production.mayautils.decorators as md

reload(md)

import lay.lca_camera_lock.functions as functions_cl

reload(functions_cl)

import stereo.findStereoCamera as fsc

reload(fsc)

import lay.utilities.cam_funcs as cam_funcs

reload(cam_funcs)

import cam_note_to_mod_pc as cntmp

reload(cntmp)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出相机"
        self.description = u"将镜头的相机输出为一个abc文件, shotgun标记镜头是静/动"
        return

    def write_log(self, content):
        try:
            import proc.log_publish_process as lpp
            reload(lpp)
            current_file = pm.sceneName().replace('\\', '/')
            publish_log_dir = os.path.dirname(current_file) + '/publish_log'
            if not os.path.exists(publish_log_dir):
                os.makedirs(publish_log_dir)
            log_file = publish_log_dir + '/' + os.path.basename(current_file)[:-3] + '.log.txt'
            log_file = log_file.replace('\\', '/')
            if not os.path.exists(log_file):
                op = open(log_file, 'w')
                op.close()
            lpp.log(log_file, content)
        except:
            self.dialog.print_log(traceback.format_exc())

    # @md.d_disableViews
    def proceed(self):
        try:
            last_v = 0
            if not hasattr(self.dialog, 'no_cam_rig'):
                self.dialog.no_cam_rig = False

            log = 'export_cam.py\n'
            self.dialog.version_dir = self.dialog.version_dir.replace('\\', '/')
            self.dialog.cam_dir = ''
            if functions_cl.is_camera_locked():
                # ignored the camera baking if the status is locked
                log += 'the camera is locked, no need to export camera\n'
                self.write_log(log)
                return ''

            if self.dialog.publish_mode == 0 and self.dialog.step['name'] != 'flo':
                cam_dir_name = 'daily_camera'
            else:
                cam_dir_name = 'camera'

            if not os.path.isdir(self.dialog.version_dir + '/' + cam_dir_name):
                os.makedirs(self.dialog.version_dir + '/' + cam_dir_name)
                log += 'make camera dir: ' + self.dialog.version_dir + '/%s\n' % cam_dir_name

            # Version mark
            f = open(self.dialog.version_dir + '/%s/info.txt' % cam_dir_name, 'w')
            f.write(self.dialog.version_name + '\n')
            f.close()
            log += 'write camera version to info.txt: ' + self.dialog.version_name + '\n'

            cam_grp = functions_cl.get_cameras_group()
            if pm.attributeQuery('notes', node=cam_grp, exists=True):
                cam_grp.attr('notes').unlock()
                cam_grp.attr('notes').set('')
                print 'remove cameras.notes'
                log += 'remove cameras.notes successfully\n'

            if self.dialog.publish_mode == 0 and self.dialog.step[
                'name'] != 'flo':  # 'daily' + 'ani'/'lay', cannot get self.dialog.cam_dir
                cam_output_info = {}
                if self.dialog.project['name'].lower() in ['pws', 'yzc'] or self.dialog.no_cam_rig:
                    err = expCam.exportCam2(path=self.dialog.version_dir + '/' + cam_dir_name,
                                            cam=self.dialog.entity['name'] + '_cam', output_info=cam_output_info)
                else:
                    cut_in = int(pm.animation.playbackOptions(q=True, minTime=True))
                    cut_out = int(pm.animation.playbackOptions(q=True, maxTime=True))

                    log += 'exportCam3\n'
                    log += self.dialog.version_dir + '/' + cam_dir_name + '\n'
                    err, _ = expCam.exportCam3(self.dialog, cut_in, cut_out,
                                               path=self.dialog.version_dir + '/' + cam_dir_name,
                                               daily_mode=True, output_info=cam_output_info, autoExtend=False)
                self.write_log(log)
                if err:
                    log += 'failed to export camera: ' + str(err) + '\n'
                    self.write_log(log)
                    return err

            else:  # 'checked' or 'downstream'
                # get rid of ai-related nodes in the raw cam file.
                raw_cam_file = self.dialog.version_dir + '/%s/' % cam_dir_name + self.dialog.entity[
                    'name'] + '_cam_raw.ma'
                try:
                    if os.path.exists(raw_cam_file):
                        cam_funcs.cleanup_cam_raw_ai_node(raw_cam_file)
                        log += 'Run function cleanup_cam_raw_ai_node successfully. \n'
                    else:
                        log += 'No raw cam, function cleanup_cam_raw_ai_node skipped. \n'
                except Exception, e:
                    log += 'cleanup_cam_raw_ai_node Failed: \n' + str(e) + '\n'

                # Duplicate camera folder
                tokens = self.dialog.version_dir.split('/')
                if not 'shot' in tokens:
                    log += 'failed to duplicate camera folder because the path does not contains shot keyword\n'
                    self.write_log(log)
                    return ""

                # record if the new cam comes from ani:
                if self.dialog.step['name'] == 'ani':
                    msg = u'\nani修改了相机: ' + self.dialog.entity['name'] + '\n'
                    self.dialog.description += msg
                if self.dialog.step['name'] == 'flo' and self.dialog.task['name'].lower() == 'final_layout':
                    self.dialog.description += u'\nflo修改了相机: {}\n'.format(self.dialog.entity['name'])

                self.write_log(log)

                if not os.path.isdir(self.dialog.version_dir + '/camera'):
                    os.makedirs(self.dialog.version_dir + '/camera')
                    log += 'make camera dir: ' + self.dialog.version_dir + '/camera\n'

                # Version mark
                f = open(self.dialog.version_dir + '/camera/info.txt', 'w')
                f.write(self.dialog.version_name + '\n')
                f.close()
                log += 'write camera version to info.txt: ' + self.dialog.version_name + '\n'

                cam_grp = functions_cl.get_cameras_group()
                if pm.attributeQuery('notes', node=cam_grp, exists=True):
                    cam_grp.attr('notes').unlock()
                    cam_grp.attr('notes').set('')
                    print 'remove cameras.notes'
                    log += 'remove cameras.notes successfully\n'

                cam_output_info = {}
                if self.dialog.project['name'].lower() in ['pws', 'yzc'] or self.dialog.no_cam_rig:
                    i = tokens.index('shot')
                    cam_root = '/'.join(tokens[:i + 3]) + '/cam/publish/'
                    log += 'camera folder: ' + cam_root + '\n'
                    if os.path.isdir(cam_root):
                        l_versions = sorted([version for version in sorted(os.listdir(cam_root))
                                             if version.startswith(self.dialog.entity['name'] + '.cam.camera.v')
                                             and version[-3:].isdigit()])
                        last_v = 0
                        if l_versions:
                            last_v = int(l_versions[-1][-3:])

                        self.dialog.cam_dir = cam_root + self.dialog.entity['name'] + (
                                    '.cam.camera.v%03d' % (last_v + 1))
                        log += 'set self.dialog.cam_dir: ' + self.dialog.cam_dir + '\n'
                    else:
                        log += 'camera folder does not exists!\n'
                        self.write_log(log)
                        return ''

                    err = expCam.exportCam2(path=self.dialog.version_dir + '/' + cam_dir_name,
                                            cam=self.dialog.entity['name'] + '_cam', output_info=cam_output_info)
                    shutil.copytree(self.dialog.version_dir + '/camera', self.dialog.cam_dir)
                    log += 'copy camera folder from ' + self.dialog.version_dir + '/camera to ' + self.dialog.cam_dir + '\n'
                    log += 'exportCam2\n'
                else:
                    cut_in = int(pm.animation.playbackOptions(q=True, minTime=True))
                    cut_out = int(pm.animation.playbackOptions(q=True, maxTime=True))

                    log += 'exportCam3\n'
                    # exportCam3 involves the shutil.copytree operation.
                    err, self.dialog.cam_dir = expCam.exportCam3(self.dialog, cut_in, cut_out,
                                                                 daily_mode=False, output_info=cam_output_info)
                    print 'err'
                    print err
                    print self.dialog.cam_dir
                    log += 'copy camera folder from ' + self.dialog.version_dir + '/camera to ' + self.dialog.cam_dir + '\n'

                if err:
                    log += 'failed to export camera: ' + str(err) + '\n'
                    self.write_log(log)
                    return err

                # tag on shotgun if the camera is animated
                if cam_output_info.has_key('animated'):
                    log += 'need to inform shotgun if the camera is animated or static\n'
                    info = self.dialog.sg.find_one('Shot', [['project', 'name_is', self.dialog.project['name']],
                                                            ['code', 'is', self.dialog.entity['name']]],
                                                   ['sg_cam_anim'])
                    if info:
                        if cam_output_info['animated']:
                            self.dialog.sg.update('Shot', info['id'], {'sg_cam_anim': 'animated'})
                            log += 'update shotgun: camera is animated\n'
                        else:
                            self.dialog.sg.update('Shot', info['id'], {'sg_cam_anim': 'static'})
                            log += 'update shotgun: camera is static\n'

                # get rid of ai-related nodes in the raw cam file.
                # raw_cam_file = self.dialog.version_dir + '/camera/' + self.dialog.entity['name']+'_cam_raw.ma'
                anim_cam_file = self.dialog.version_dir + '/camera/' + self.dialog.entity['name'] + '_cam_anim.ma'
                os.system("chmod 777 -R * %s" % self.dialog.version_dir)
                try:
                    if os.path.exists(anim_cam_file):
                        cam_funcs.cleanup_cam_raw_ai_node(anim_cam_file)
                        log += 'Run function cleanup_cam_anim_ai_node successfully. \n'
                    else:
                        log += 'No raw cam, function cleanup_cam_anim ai_node skipped. \n'
                except Exception, e:
                    log += 'cleanup_cam_raw_ai_node Failed: \n' + str(e) + '\n'

                # Duplicate camera folder
                tokens = self.dialog.version_dir.split('/')
                if not 'shot' in tokens:
                    log += 'failed to duplicate camera folder because the path does not contains shot keyword\n'
                    self.write_log(log)
                    return ""
                i = tokens.index('shot')
                cam_root = '/'.join(tokens[:i + 3]) + '/cam/publish/'
                if os.path.isdir(cam_root):
                        l_versions = sorted([version for version in sorted(os.listdir(cam_root))
                                             if version.startswith(self.dialog.entity['name'] + '.cam.camera.v')
                                             and version[-3:].isdigit()])
                        last_v = 0
                        if l_versions:
                            last_v = int(l_versions[-1][-3:])
                self.cam_root = cam_root
                self.cam_output_info = cam_output_info
            self.last_v =last_v
                
            shot_name = self.dialog.entity['name']
            
            if self.last_v != 1:
                if cam_output_info.has_key('animated'):
                    cam_type = self.cam_output_info['animated']
                else:
                    cam_type = False
                new_camera_version_dir = self.cam_root + shot_name + (
                                        '.cam.camera.v%03d' % (self.last_v)+'/{}_data.txt'.format(shot_name))
                
                last_camera_version_dir = self.cam_root + shot_name + (
                                        '.cam.camera.v%03d' % (self.last_v-1)+'/{}_data.txt'.format(shot_name))
                note_flag =True
                checker = CheckCamTool()
                note_flag = checker.check_cam(last_camera_version_dir,new_camera_version_dir,cam_type)
                log += ("\nnote_flag: {}\n".format(note_flag))
            else:
                note_flag = True
            
            if not note_flag:
                pass
            else:
                log += 'We will note to mod\n' 
                cntmp.main(self.dialog) # 有相机生成，就抄送 note 给 模型外包制片，目前只针对 ani，flo 环节
            self.write_log(log)
            return ''
        except:
            self.write_log(str(traceback.format_exc()) + '\n')
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
    
    
from collections import OrderedDict
class CheckCamTool(object):
    # Script by Jamboo
    # this class crated by modelers' need
    # Date : 12/2024
    """
    以下是给到的需求原文:
        输出相机判定是否位移或者旋转过大,才通知mod
        1. 焦距比原相机减小了的
        2. 新增旋转超过20度的 (rotate XYZ)
            (判断建议:如果是定镜头,旋转轴加减超过数值20的,可以提示;
            如果是运动镜头,起始帧减了超过20的,或结束帧超过20了的,可以提示)
    
    """
    
    def __init__(self):
        self.message = ""
        self.key_fields = ['rx','ry','rz','focalLength']
        self.note_flag = True
        self.note_flag_animated = False #[NOTE]:动态镜头变化通知flg
        self.note_flag_focalLength = False #[NOTE]:静态镜头变化通知flg
        self.note_flag_static = False#[NOTE]:焦距变化通知flg

    
    def check_cam(self,last_cam_info_file_path,new_cam_info_file_path,cam_type):
        #type: (str,str,bool) -> str
        # [NOTE] :获取上一个版本的cam信息
        last_cam_info = self.get_frame_dict(last_cam_info_file_path) #type: dict
        #[NOTE] : 获取当前的cam信息
        new_cam_info = self.get_frame_dict(new_cam_info_file_path) #type: dict
        if  not last_cam_info or not new_cam_info:
            return self.note_flag
        #[NOTE]: 获取较小范围内的time range
        time_range = self.get_time_range(last_cam_info,new_cam_info) #type: list[int]
        
        self.cam_type = cam_type
        #[NOTE]: 不管动还是静镜头 都检查焦距
        for attr in self.key_fields:
            last_field_value = last_cam_info[attr] #type:dict[int,str]
            new_field_value = new_cam_info[attr] #type:dict[int,str]

            for frame in range(*time_range):
                if attr == "focalLength":
                    if new_field_value[frame] < last_field_value[frame]:
                        focalLength_difference = abs(new_field_value[frame] - last_field_value[frame])
                        #[NOTE]: 默认不通知，如果focal length有变化则通知
                        if focalLength_difference != 0 :
                            self.note_flag_focalLength = True
                else:
                    if self.cam_type != True:
                        #[NOTE]: 如果前后两帧的transform不一致则为动镜头
                        if frame != time_range[0]:
                            if new_field_value[frame] != new_field_value[frame-1]:
                                self.cam_type = True
                    
        
        if not self.cam_type:
            self.check_static_cam(last_cam_info,new_cam_info)
        if self.cam_type:
            self.check_animated_cam(last_cam_info,new_cam_info)
            
        self.note_flag = any([self.note_flag_animated,self.note_flag_static,self.note_flag_focalLength])
        # return [self.note_flag_animated,self.note_flag_static,self.note_flag_focalLength]
        return self.note_flag
    
    def get_time_range(self,last_cam_info,new_cam_info):
        """获取帧数范围相对小的帧范围"""
        last_start_frame = last_cam_info['time_start'] #type:int
        last_end_frame = last_cam_info['time_end'] #type:int

        
        new_start_frame = new_cam_info['time_start'] #type:int
        new_end_frame = new_cam_info['time_end'] #type:int

        if last_end_frame < new_end_frame:
            end_frame = last_end_frame
        else:
            end_frame = new_end_frame
            
        if last_start_frame > new_start_frame:
            start_frame = last_start_frame
        else:
            start_frame = new_start_frame
            
        time_range = [start_frame,end_frame] #type:list[int,int]

        return time_range
        
    
    def check_static_cam(self,last_cam_info,new_cam_info):
        """检查定镜头:旋转超过20度"""
        time_range = self.get_time_range(last_cam_info,new_cam_info)
        for attr in self.key_fields:

            last_field_value = last_cam_info[attr] #type:dict[int,str]
            new_field_value = new_cam_info[attr] #type:dict[int,str]
            #[NOTE]： 默认不通知，如果有旋转超过20的则通知
            for frame in range(*time_range):
                compare = abs(new_field_value[frame]-last_field_value[frame])
                if compare >= 20:
                    self.note_flag_static = True
                    break
            if self.note_flag_static == True:
                break
        return self.note_flag
        
                        
        
    def check_animated_cam(self,last_cam_info,new_cam_info):
        """检查运动镜头:如果起始帧或结束帧增减超过20帧通知mod"""
        #[NOTE]:获取frame范围进行比较
        last_start_frame = last_cam_info['time_start'] #type:int
        last_end_frame = last_cam_info['time_end'] #type:int
        new_start_frame = new_cam_info['time_start'] #type:int
        new_end_frame = new_cam_info['time_end'] #type:int

        # [NOTE]: 动态镜头如果差值>20则通知
        if all([abs(new_start_frame - last_start_frame) >= 20,abs(new_end_frame - last_end_frame) >= 20]):
            self.note_flag_animated = True
        return self.note_flag_animated

        
    def get_frame_dict(self,info_file_path):
        """获取写到服务器的相机信息"""
        
        if not os.path.exists(info_file_path):
            self.message = '\n[[get_frame_dict] No such file or directory:]: {}\n'.format(info_file_path)
            return
            # raise Exception(self.message )
        
        with open(info_file_path,'r') as file:
            info_dict = {} #type:dict[str:OrderedDict]
            data = file.readlines()
            for info in data:
                # [NOTE] : 获取相机记录出的起始结束帧
                if info.startswith("time:"):
                        time_range = info.split(":")[-1].replace('\n','')
                        time_start = time_range.split(' ')[0] #type: str
                        time_end = time_range.split(' ')[-1] #type: str
                        
                        self.time_start = int(float(time_start))
                        self.time_end= int(float(time_end))
                        info_dict.update({"time_start": self.time_start})
                        info_dict.update({"time_end": self.time_end})
                        
                info_key = info.split(":")[0].replace('\n','')    
                if info_key in  self.key_fields:
                #[NOTE]: 筛选出 tx,ty,tz,rx,ry,rz
                    info_values = info.split(":")[-1].replace('\n','')
                    info_value_list = info_values.split(" ")
                    
                    # [NOTE]: 每一帧的frame 和对应的attr值
                    frame_infoValue_dict = OrderedDict() # type: OrderedDict[int:float]
                    for frame in range(self.time_start,self.time_end+1):
                        attr_value = float(info_value_list[frame-self.time_start])
                        frame_infoValue_dict.update({frame:attr_value})
                    # [NOTE] : 属性名称和对应的 {帧:值} 字典    
                    info_dict.update({info_key:frame_infoValue_dict})  
        return info_dict