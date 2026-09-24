# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description:
#
############################################

import os
import sys
import traceback
import pprint

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"刷新 shotgun sequence playlsit"
        self.description = u"在shotgun上每个场都有播放最新版本的播放列表。新版本出现后应该刷新。"
        return

    def update_playlist(self, pl ):
        if pl['locked']:
            self.dialog.sg.update('Playlist', pl['id'], {'locked':False})

        l_versions = pl['versions']
        for version in l_versions:
            if version['name'].startswith(self.dialog.entity['name']):
                l_versions.remove(version)
        self.dialog.print_log('v_info:' + str(self.dialog.v_info))

        l_versions.append(self.dialog.v_info)
        self.dialog.sg.update('Playlist', pl['id'], {'versions': l_versions})
        self.dialog.print_log('update playlist id:' + str(pl['id']))

        # Set sort order
        filters = [['playlist', 'is', {'type':'Playlist', 'id':pl['id']}]]
        fields = ['playlist.Playlist.code', 'sg_sort_order', 'version.Version.code']
        l_links = self.dialog.sg.find('PlaylistVersionConnection', filters, fields)

        d_links = {}
        for link in l_links:
            d_links[link['version.Version.code']] = link

        l_v_names = sorted(d_links.keys())
        for i in range(len(l_v_names)):
            v_name = l_v_names[i]
            self.dialog.sg.update('PlaylistVersionConnection', d_links[v_name]['id'], {'sg_sort_order': i+1})
            self.dialog.print_log('update PlaylistVersionConnection:' + str(d_links[v_name]['id']))

        return


    def proceed(self):
        try:
            l_all_depts = ['lay', 'ani', 'cfx', 'flo', 'lgt', 'pfx']
            d_all_depts = {'lay':['rough_layout'], 'ani':['animation'], 'cfx':['hair', 'cloth'], 'flo':['final_layout'], 'lgt':['lighting', 'lgt_rig'], 'pfx':['paint_fix', 'floating_window']}

            if not self.dialog.step['name'] in l_all_depts:
                return ""

            if not self.dialog.task['name'].lower() in d_all_depts[self.dialog.step['name']]:
                return ""

            l_pls = self.dialog.sg.find('Playlist', [['tag_list', 'is', 'Sequence'], ['project', 'is', self.dialog.project]], ['tag_list', 'code', 'versions', 'locked'])

            for pl in l_pls:
                tokens_pl = pl['code'].split('.')
                if not self.dialog.entity['name'].startswith( tokens_pl[1] ):
                    continue

                if self.dialog.step['name'] == tokens_pl[2]:
                    self.update_playlist( pl )

                if tokens_pl[2] == 'all':
                    old_version = ''
                    for v_info in pl['versions']:
                        if v_info['name'].startswith( self.dialog.entity['name'] ):
                            old_version = v_info['name']

                    if old_version == '':
                        self.update_playlist(pl)
                    else:
                        tokens_versions = old_version.split('.')
                        if not tokens_versions[1] in l_all_depts:
                            self.update_playlist(pl)

                        i = l_all_depts.index(tokens_versions[1])
                        j = l_all_depts.index(self.dialog.step['name'])
                        if i <= j:
                            self.update_playlist(pl)                    

            #d_version = {'project':self.dialog.project, 'entity':self.dialog.entity, 'sg_task':self.dialog.task,'code':self.dialog.version_name, 'description':self.dialog.description, 'user':self.dialog.user, 'sg_version_folder':{ 'local_path': local_path, 'name':self.dialog.version_name, 'content_type':None, 'link_type':'local'} , 'sg_version_type': d_v_type[self.dialog.publish_mode], 'tag_list':[self.dialog.version_tag], 'created_by':self.dialog.user}


            #self.dialog.v_info 
            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

