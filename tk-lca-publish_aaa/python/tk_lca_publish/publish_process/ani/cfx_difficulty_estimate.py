# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: XiangQuan
#
# Date: 2015.08
#
# Description:
#
############################################

import os
import sys
import pprint
import traceback
import math
from xml.dom.minidom import Document, parse
from xml.etree import ElementTree

import maya.cmds as cmds
import pymel.core as pm

ASSET_COUNT = [6, 14]            #<=6 B, <=14 A, e.g. 7: B, 15:A
TRANS_SPEED = [2, 8, 16]        #<=2 D; 2-8(=8) C; 8-16(=16) B; >=16 A
ROTATE_SPEED = [5, 15, 25]      #<=5 D; 5-15 C;15-25 B; >=25 A
SCORE = [1, 3, 6, 10]           #D, C, B, A

SCENE_INFO_KEY = 'scene_info'
TRANSFORM_CURVE = 'spine_M_root_ctrl'
SPEC_FINAL_SCORE = 'NO CHAR'

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"预判cfx任务的难度级别"
        self.description = u"根据动画场景的元素和数据，预判cfx任务的难度级别D/C/B/A"

    def proceed(self):
        try:
            startF, endF, duration = self.get_frame_range()
            chrs = self.get_all_chrs()
            chrs_count = len(chrs)
            print startF, endF, duration, chrs_count, chrs
            chrs_count_score = self.calc_assets_count_score(chrs_count)
            
            scene_score = -1.0
            asset_data = {SCENE_INFO_KEY:[startF, endF, chrs_count]}
            for single_chr in chrs:
                single_chr = str(single_chr)
                char_name = single_chr.replace(':master', '')
                
                #get a character's difficulty
                difficulty, difficulty_score = self.calc_asset_difficulty_score(single_chr)
                #difficulty, difficulty_score = 1, 1.2
                spine_M_root_ctrl = self.get_spine_M_root_ctrl(single_chr)
                loc_name, p_constraint= self.__create_parentConstraint_locator(spine_M_root_ctrl)
                if not loc_name and not p_constraint:
                    continue
                
                #calculate data per frame, since we only care about speed, we only record largest translation and rotation
                largest_dist = 0
                largest_rotate = 0
                for frame in range(int(startF), int(endF), 1):
                    dist = self.get_tranlation_perframe(loc_name, frame)
                    rotate = self.get_rotation_perframe(loc_name, frame)
                    if dist > largest_dist:
                        largest_dist = dist
                    if rotate > largest_rotate:
                        largest_rotate = rotate
                
                if largest_dist == 0 and largest_rotate == 0:
                    continue
                
                transform_score, dist_score, rotate_score = self.calc_transform_score(largest_dist, largest_rotate)
                #final_score = chrs_count_score * 0.2 + transform_score * 0.5 + difficulty_score * 0.3
                final_score = chrs_count_score + transform_score * difficulty_score
                if final_score > scene_score:
                    scene_score = final_score
                
                #record check result
                asset_data[single_chr] = [difficulty, difficulty_score, largest_dist, largest_rotate]
                
                #delete unused locator and parentConstrain
                self.__del_parentConstraint_locator(loc_name, p_constraint)
                
                #print '[', single_chr, ']'
                #print 'difficulty: ', difficulty, difficulty_score
                #print 'chrs_count: ', chrs_count, chrs_count_score
                #print 'largest_dist: ', largest_dist, dist_score
                #print 'largest_rotate: ', largest_rotate, rotate_score
                #print 'transform_score: ', transform_score
                #print 'final_score: ', final_score
                #print '==================================================='
            
            final_level = ''
            if scene_score < 0.0:
                final_level = SPEC_FINAL_SCORE
            elif scene_score >=0.0 and scene_score < 3.0:
                final_level = 'D'
            elif scene_score >= 3.0 and scene_score < 7.0:
                final_level = 'C'
            elif scene_score >= 7.0 and scene_score < 18.5:
                final_level = 'B'
            elif scene_score >= 18.5:
                final_level = 'A'
            
            asset_data[SCENE_INFO_KEY].append(str(scene_score))
            asset_data[SCENE_INFO_KEY].append(final_level)
            
            #recored result
            self.write_to_xml(asset_data)
            
            #read from the xml, write level to related cfx tasks
            self.write2task()
            
            return ""
        except:
            return traceback.format_exc()
        
    def calc_assets_count_score(self, chrs_count):
        '''
        '''
        asset_count = ASSET_COUNT[:]        #shallow copy
        asset_count_score = 0
        if asset_count != 0:
            asset_count.append(chrs_count)
            asset_count.sort()
            asset_index = asset_count.index(chrs_count)
            asset_count_score = self.get_assets_count_level(asset_index, chrs_count)
            
        return asset_count_score
    
    def get_assets_count_level(self, index, chrs_count):
        '''
        ASSET_COUNT = [6, 9]
        '''
        asset_count_score = 0
        if index == 0:      #<= 6
            asset_count_score = 1    # D or C
        elif index == 1:    #7-20
            asset_count_score = 6       #B
        elif index == 2:    # > 20
            asset_count_score = 15        #A
        
        return asset_count_score
    
    def calc_transform_score(self, dist, rotate):
        '''
        '''
        trans_speed = TRANS_SPEED[:]        #shallow copy
        rotate_speed = ROTATE_SPEED[:]
        
        trans_score = 0
        if dist != 0:
            trans_speed.append(dist)
            trans_speed.sort()
            trans_index = trans_speed.index(dist)    #when dist has the same value with an elem, return the first index
            trans_score = self.get_translate_score(trans_index, dist)
        
        rotate_score = 0
        if rotate != 0:
            rotate_speed.append(rotate)
            rotate_speed.sort()
            rotate_index = rotate_speed.index(rotate)    #when dist has the same value with an elem, return the first index
            rotate_score = self.get_rotate_score(rotate_index, rotate)
        
        #only keep the larger value
        if rotate_score > trans_score:
            final_score = rotate_score
        else:
            final_score = trans_score
        
        return final_score, trans_score, rotate_score
    
    def get_translate_score(self, data_index, data_speed):
        '''
        TRANS_SPEED = [2, 8, 16]        #<=2 D; 2-8(=8) C; 8-16(=16) B; >=16 A
        Score_range:  1, 3, 6, 10
        '''
        level_score = 0
        if data_index == 0:
            level_score = 0.5 * data_speed     #D
        elif data_index == 1:
            level_score = 1 + 0.34 * (data_speed - 2.0)     #C
        elif data_index == 2:
            level_score = 3 + 0.375 * (data_speed - 8.0)    #B
        elif data_index == 3:
            level_score = 6 + 0.4 * (data_speed - 16)       #A
            
        return level_score
    
    def get_rotate_score(self, data_index, data_speed):
        '''
        ROTATE_SPEED = [5, 15, 25]      #<=5 D; 5-15 C;15-25 B; >=25 A
        Score_range:   1, 3,  6,  10
        '''
        level_score = 0
        if data_index == 0:
            level_score = 0.2 * data_speed     #D
        elif data_index == 1:
            level_score = 0.2 * data_speed     #C
        elif data_index == 2:
            level_score = 3 + 0.3 * (data_speed - 15)     #B
        elif data_index == 3:
            level_score = 6 + 0.4 * (data_speed - 25)    #A
            
        return level_score
    
    def calc_asset_difficulty_score(self, single_chr):
        '''
        e.g. single_chr = 'atang:master'
        '''
        asset_ma = pm.referenceQuery(single_chr, filename = True, shortName = True)
        asset_name = os.path.splitext(asset_ma)[0]
        chr_info = self.dialog.sg.find_one('Asset', [['project', 'is', {'type': 'Project', 'id': self.dialog.project['id']}],['code', 'is', asset_name]], \
                                           ['sg_difficulty'])
        difficulty = chr_info['sg_difficulty']
        print single_chr, chr_info, 'difficulty', difficulty
        if difficulty is None:
            difficulty = 4
        chr_difficulty = int(difficulty)
        chr_difficulty_score = self.get_asset_difficulty_score(chr_difficulty)
        
        return chr_difficulty, chr_difficulty_score
    
    def get_asset_difficulty_score(self, difficulty):
        '''
        '''
        if difficulty is None:
            difficulty = 4
        
        score = 0.6 + (5 - difficulty) * 0.15
        
        return score
    
    def get_frame_range(self):
        '''
        '''
        endFrame = pm.animation.playbackOptions(query = True,animationEndTime = True)       #float
        startFrame = pm.animation.playbackOptions(query = True,animationStartTime = True)
        duration = endFrame - startFrame
        
        return startFrame, endFrame, duration
    
    def get_all_chrs(self):
        '''
        '''
        if not pm.objExists('assets|chr'):
            return []
        
        #chrs = pm.listRelatives('assets|chr', children = True)      #nt.Transform()
        chrs = pm.listRelatives('assets|chr', allDescendents = True, type = 'transform')      #in case some real characters are grouped together under a transform
        valid_chrs = []
        for single_chr in chrs:
            if single_chr.endswith('master') and pm.getAttr(single_chr + '.visibility'):
                valid_chrs.append(single_chr)
        
        return valid_chrs
    
    def get_spine_M_root_ctrl(self, chr_node):
        '''
        get the name of spine rigging(the four directions arrows circle, e.g. atang:spine_M_root_ctrl)
        e.g. chr = u'teashop_boss:master'
        '''
        spine_M_root_ctrl = None
        sub_chrs = pm.listRelatives(chr_node, children = True)
        for sub_chr in sub_chrs:
            if sub_chr.endswith(':rig'):
                all_trans = pm.listRelatives(sub_chr, allDescendents = True, type = 'joint')
                #all_trans = pm.listRelatives(sub_chr, allDescendents = True, type = 'transform')
                for trans in all_trans:
                    if trans.endswith(TRANSFORM_CURVE):
                        spine_M_root_ctrl = trans
                        break
                break
        return spine_M_root_ctrl 
    

    def get_tranlation_perframe(self, loc_name, crntFrame):
        '''
        calculate distance between two adjacent frames
        '''
        transx = pm.getAttr(loc_name + '.translateX', time = crntFrame)
        transy = pm.getAttr(loc_name + '.translateY', time = crntFrame)
        transz = pm.getAttr(loc_name + '.translateZ', time = crntFrame)
        
        next_transx = pm.getAttr(loc_name + '.translateX', time = crntFrame + 1)
        next_transy = pm.getAttr(loc_name + '.translateY', time = crntFrame + 1)
        next_transz = pm.getAttr(loc_name + '.translateZ', time = crntFrame + 1)
        
        dist = math.sqrt(math.pow(transx - next_transx, 2) + math.pow(transy - next_transy, 2) + math.pow(transz - next_transz, 2))
        return dist
    
    def get_rotation_perframe(self, loc_name, crntFrame):
        '''
        calculate rotation degree between two adjacent frames
        return the largest one only
        '''
        rotatex = pm.getAttr(loc_name + '.rotateX', time = crntFrame)
        rotatey = pm.getAttr(loc_name + '.rotateY', time = crntFrame)
        rotatez = pm.getAttr(loc_name + '.rotateZ', time = crntFrame)
        
        next_rotatex = pm.getAttr(loc_name + '.rotateX', time = crntFrame + 1)
        next_rotatey = pm.getAttr(loc_name + '.rotateY', time = crntFrame + 1)
        next_rotatez = pm.getAttr(loc_name + '.rotateZ', time = crntFrame + 1)
        
        diffx = abs(rotatex - next_rotatex)
        diffy = abs(rotatey - next_rotatey)
        diffz = abs(rotatez - next_rotatez)
        sorted_r = sorted([diffx, diffy, diffz])
        
        return sorted_r[-1]
    
    def __get_st_parents(self, spine_M_root_ctrl):
        '''
        '''
        st_long = cmds.ls(str(spine_M_root_ctrl), long = True)[0]
        count = len(st_long.split('|'))
        st_parents = []
        #get rid of '', 'assets', 'chr', '...:master', '...:rig'
        for i in range(0, count - 5):
            p_name = st_long.rsplit('|', i)[0]
            short_p = cmds.ls(p_name, shortNames = True)[0]
            st_parents.append(short_p)
            
        return st_parents
    
    def __create_parentConstraint_locator(self, spine_M_root_ctrl):
        '''
        parentConstraint a locator and the spine_M_root_ctrl to collect world transformation
        '''
        try:
            locator_name = pm.spaceLocator(position = (0, 0, 1))
            p_constraint = pm.parentConstraint(spine_M_root_ctrl, locator_name)
        except:
            print 'No spine_M_root_ctrl', 'exists. Skip it'
            if pm.objExists(locator_name):
                pm.delete(locator_name)
            
            locator_name = None
            p_constraint = None
        
        return locator_name, p_constraint
    
    def __del_parentConstraint_locator(self, locator_name, p_constraint):
        '''
        delete unused locator and parentConstraint node
        '''
        try:
            pm.delete(locator_name)
            if pm.objExists(p_constraint):
                pm.delete(p_constraint)
        except:
            print '__del_parentConstraint_locator Error:', 
            print traceback.format_exc()
    
    def write_to_xml(self, asset_data):
        '''
        write result to cfx_difficulty.xml, should consider whether the file exists or not
        asset_data = {'scene_info':[startF, endF, chrs_count], 
                      'atang:master':[difficulty, difficulty_score, largest_dist, largest_rotate],}
        '''
        start_frame = asset_data[SCENE_INFO_KEY][0]
        end_frame = asset_data[SCENE_INFO_KEY][1]
        chrs_count = asset_data[SCENE_INFO_KEY][2]
        scene_score = asset_data[SCENE_INFO_KEY][3]
        scene_level = asset_data[SCENE_INFO_KEY][4]
        
        #basename = os.path.basename(pm.sceneName())
        #shotname = basename.split('.', 1)[0]
        #dirname = os.path.dirname(pm.sceneName())
        #levelname = dirname.rsplit('/', 1)[-1]
        #xml_path = self.dialog.version_dir + '/' + levelname + '_' + shotname +'.xml'
        xml_path = self.dialog.version_dir + '/difficulty_level.xml'
        #xml_path= '/mnt/work/home/xiangquan/maya2015/xml/TPR/' + shotname + '.xml'

        dom = Document()
        root_dom = dom.createElement('anim')
        root_dom.setAttribute('start', str(int(start_frame)))
        root_dom.setAttribute('end', str(int(end_frame)))
        root_dom.setAttribute('chrsCount', str(int(chrs_count)))
        root_dom.setAttribute('sceneScore', str(scene_score))
        root_dom.setAttribute('sceneLevel', scene_level)
        dom.appendChild(root_dom)
        
        for asset in asset_data:
            if asset == SCENE_INFO_KEY:
                continue
            dom_elem = dom.createElement('chr')
            dom_elem.setAttribute('name', str(asset))
            dom_elem.setAttribute('difficulty', str(asset_data[asset][0]))
            dom_elem.setAttribute('largestDist', str(asset_data[asset][1]))
            dom_elem.setAttribute('largestDist', str(asset_data[asset][2]))
            dom_elem.setAttribute('largestRotate', str(asset_data[asset][3]))
            root_dom.appendChild(dom_elem)
            
        #just formatting output xml
        pretty_text = dom.toprettyxml(indent = '    ',  newl = '')
        final_text = pretty_text.replace('        ',  '    ')
        final_text = final_text.replace('>    <',  '>\n    <')
        final_text = final_text.replace('><', '>\n<')
        
        f = open( xml_path, 'w')
        f.write(final_text)
        f.close()
    
    def get_process_name(self):
        return self.process_name
    
    def get_description(self):
        return self.description
    
#######################################################
#
# Write calculated result to Shotgun
#
#######################################################
    def read_difficulty_level(self):
        #op = open(#xml_path= '/mnt/work/home/xiangquan/maya2015/xml/TPR/' + shotname + '.xml' 'r')
        diff_level_file = self.dialog.version_dir + '/difficulty_level.xml'
        if not os.path.exists(diff_level_file):
            return None
        
        op = open(diff_level_file, 'r')
        xml_text = op.read()
        op.close()
        
        root = ElementTree.fromstring(xml_text)
        difficulty_level = root.attrib['sceneLevel']
        
        return difficulty_level
    
    def get_task_difficulty(self):
        '''
        '''
        #print 'shot: ', self.dialog.entity
        filters = [['project', 'is', {'type': 'Project', 'id': self.dialog.project['id']}],
                   ['entity', 'is', self.dialog.entity], 
                   {'filter_operator':'any', 
                    'filters':[['content', 'is', 'hair'], ['content', 'is', 'cloth']]
                    }
                   ]
        chr_info = self.dialog.sg.find('Task', filters, ['sg_difficulty'])
        print chr_info
        try:
            diff_0 = chr_info[0]['sg_difficulty']
            id_0 = chr_info[0]['id']
        except:
            diff_0 = 'No Task'
            id_0 = None
        
        try:
            diff_1 = chr_info[1]['sg_difficulty']
            id_1 = chr_info[1]['id']
        except:
            diff_1 = 'No Task'
            id_1 = None
    
        return diff_0, diff_1, id_0, id_1
    
    def write2task(self):
        '''
        '''
        diff_0, diff_1, id_0, id_1 = self.get_task_difficulty()
        if diff_0 == 'No Task' and diff_1 == 'No Task':
            return
            
        difficulty_level = ''
        if not diff_0 or not diff_1:
            difficulty_level = self.read_difficulty_level()
        if difficulty_level is None or difficulty_level == SPEC_FINAL_SCORE:
            #print 'no cfx difficulty'
            return
            
        data = {'sg_difficulty': difficulty_level}
        if not diff_0:
            self.dialog.sg.update('Task', id_0, data)
            print 'write to task', id_0
        elif diff_0 == 'No Task':
            print 'task does not exist'
        else:
            print 'value already exists'
        
        if not diff_1:
            self.dialog.sg.update('Task', id_1, data)
            print 'write to task', id_1
        elif diff_1 == 'No Task':
            print 'task does not exist'
        else:
            print 'value already exists'
            
    


