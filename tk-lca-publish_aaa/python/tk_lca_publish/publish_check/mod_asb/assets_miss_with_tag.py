# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: Check to see if any vertice are overlapping to each other.
#
########################################################################################

import traceback
import os
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as om
import production.pipeline.lcProdProj as lcp
import re
import sys
import json
from xml.etree import ElementTree

import pymongo


# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"和上一版本的资产有变动并且有shotgun标签。"
        self.description = u"动画操作过的资产会打上shotgun标签，防止资产丢失。skip tag: skip_ani_lock"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return
    
    def get_assets_from_xml(self, mesh_xml):
        mesh_dict = {}
        tree = ElementTree.parse(mesh_xml)
        root = tree.getroot()
        all_nodes = root.findall(".//attribute[@name='fullPath']")
        for node in all_nodes:
            full_path = node.attrib['value']
            if full_path.endswith('AR'):
                asset_name = full_path.strip('_AR').rsplit('|', 1)[1].split(':')[-1]
                asset_name = re.split('\d+$', asset_name)[0]
                mesh_dict[full_path] = asset_name
        return mesh_dict
    
    def get_asset_shotgun_info(self, asset):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list', 'sg_remark', 'sg_chinese'])
        return asset_info
    
    def get_anifile_by_value(self, dict, value):
        result = []
        values = dict.values()
        for sub_dir in values:
            for k, v in sub_dir.items():
                if '_id' == k:
                    continue
                if v == value or value in v:
                    result.append(sub_dir['file'])
        return result

    def get_info_from_db(self, proj_name, asset_name):
        lca_db_host = '10.0.8.157'
        lca_db_port = 27017
        lca_db_username = 'admin'
        lca_db_password = '123456'

        db_name = 'lca_ani_lock_db'
        mongo_client = pymongo.MongoClient(host=lca_db_host, port=lca_db_port,username=lca_db_username,password=lca_db_password)
        ani_lock_db = mongo_client.get_database(db_name)
        collection_ani_lock = ani_lock_db.get_collection(proj_name)
        info_cursor = collection_ani_lock.find({'asset_name': asset_name})
        info = {}

        for f in info_cursor:
            info.update({f['shot_name']: f})
        return info

    
    def run_check(self):
        try:
            # json_file_dir = 'Z:/trash/ani_lock_assets/' + self.dialog.project['name'].lower()
            
            ast_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]],
                                               ['sg_asset_type', 'code'])
            print ast_info
            asset_n = ast_info['code']
            # add skip tag check
            sg_info = self.get_asset_shotgun_info(asset_n)
            # sg_remark = sg_info['sg_remark']
            if 'skip_ani_lock' in sg_info['tag_list']:
                return ""
            #
            mod_path = 'Z:/projects/{poj}/asset/{typ}/{ast}/mod/publish/{ast}.mod.model'.format(
                poj=self.dialog.project['name'].lower(),
                typ=ast_info['sg_asset_type'],
                ast=asset_n)
            # print mod_path
            # if has short xml,use short
            short_xml = mod_path + '/scene_graph_xml/' + asset_n + '.short.xml'
            
            if os.path.exists(short_xml) or os.path.exists(short_xml.replace('Z:/', '/mnt/proj/')):
                mesh_xml = short_xml
            else:
                mesh_xml = mod_path + '/scene_graph_xml/' + asset_n + '.xml'
            if sys.platform.startswith('linux'):
                mesh_xml = mesh_xml.replace('Z:/', '/mnt/proj/')
                # json_file_dir = json_file_dir.replace('Z:/', '/mnt/proj/')
            
            if not os.path.isfile(mesh_xml):
                return ""
            
            err = ''
            last_xml_assets_dict = self.get_assets_from_xml(mesh_xml)
            # print last_xml_assets_dict
            for full_path in last_xml_assets_dict:
                # 相较于上一版缺少资产才会进行ani_lock的检查
                if not pm.objExists(full_path):
                    asset_name = last_xml_assets_dict[full_path]
                    # print asset_name
                    sg_info = self.get_asset_shotgun_info(asset_name)
                    if not sg_info:
                        return u"上一版asb中的：%s 已在当前项目中删除，请联系组长及TD处理"%asset_name
                    # sg_remark = sg_info['sg_remark']
                    if 'ani_lock' in sg_info['tag_list']:
                        print "detect animation lock!"
                        # find ani asset information!!
                        # json_file = "%s/%s.json" % (json_file_dir, asset_name)
                        db_info = self.get_info_from_db(self.dialog.project['name'].lower(), asset_name)
                        # if not os.path.exists(json_file) and not db_info:
                        if not db_info:
                            print "No information about ani_lock was found for asset %s" % asset_name
                            return "No information about ani_lock was found for asset %s" % asset_name

                        ###
                        # ani_paths = list(set([x['node'] for x in info.values()]))
                        ani_paths = []

                        # if db_info:
                        #     info = db_info
                        # else:
                        #     try:
                        #         if os.path.exists(json_file):
                        #             with open(json_file, 'r') as f:
                        #                 info = json.load(f)
                        #     except Exception as e:
                        #         traceback.print_exc()
                        #         msg = u'{}的ani_lock的json文件出问题了，请把报错信息发送给TD。'.format(asset_name)
                        #         return msg

                        for x in db_info.values():
                            if 'node_list' in x:
                                ani_paths.extend(x['node_list'])
                            else:
                                ani_paths.append(x['node'])
                        
                        ani_paths = list(set(ani_paths))
                        
                        err_tmp = ''
                        for ani_path in ani_paths:
                            tga_path = '|'.join([x.split(':')[-1] for x in ani_path.split('|')])
                            sor_path = '|'.join([x.split(':')[-1] for x in full_path.split('|')])
                            if asset_n in tga_path and (tga_path.endswith(sor_path)):

                                anifiles = self.get_anifile_by_value(db_info, ani_path)
                                
                                ani_info = ': '
                                if anifiles:
                                    for anifile in anifiles:
                                        tokens = anifile.rsplit('/', 1)[1].split('.')
                                        ani_info += tokens[0] + '.' + tokens[-2] + ' '
                                        
                                err_tmp += u"ani_path  : %s \n而且已经在 | 动画镜头%s | Key过，如果需要修改请联系动画\n\n" % (
                                tga_path, ani_info)
                        
                        if err_tmp:
                            if sg_info['sg_chinese']:
                                err += u"资产 : %s [%s]  和上一版层级不一致.\nasb_path : %s \n" % (
                                asset_name, sg_info['sg_chinese'].decode('utf-8'), full_path) + err_tmp
                            else:
                                err += u"资产 : %s  和上一版层级不一致.\nasb_path : %s \n" % (
                                asset_name, full_path) + err_tmp
            
            if err:
                return err
            
            return ""
        except:
            return traceback.format_exc()
    
    def run_fix(self):
        '''Auto Fix'''
        try:
            return ''
        
        except:
            return traceback.format_exc()
    
    def get_check_name(self):
        return self.check_name
    
    def get_description(self):
        return self.description
    
    def get_auto_fix(self):
        return self.auto_fix
    
    def get_duty(self):
        return self.duty

