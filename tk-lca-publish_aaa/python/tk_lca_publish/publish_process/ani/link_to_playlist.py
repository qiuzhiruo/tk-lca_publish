# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.01
#
# Description: Link to playlist
#
############################################

import os
import sys
import traceback
import pprint
import datetime

import pymel.core as pm

PLAYLIST_NAME = '%s.%s.daily review with Amp'

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"关联到动画师给家康退卡的Playlist"
        self.description = u"关联到动画师给家康退卡的Playlist"
        return


    def proceed(self):
        try:
            result = pm.windows.confirmDialog(message=u'需要添加到哪天的Playlist?',
                                              button=[u'今天', u'明天', u'不需要'],
                                              defaultButton=u'今天',
                                              cancelButton=u'不需要',
                                              dismissString=u'不需要')
            if result == u'不需要':
                return ""

            now = datetime.datetime.now()
            date = datetime.date(now.year, now.month, now.day)
            if result == u'明天':
                date += datetime.timedelta(days=1)

            datecode = date.strftime('%Y-%m-%d')
            name = PLAYLIST_NAME % (self.dialog.project.get('name').upper(), datecode)
            playlist = self.dialog.sg.find_one('Playlist',
                                               [['project', 'is', self.dialog.project],
                                                ['code', 'is', name]])

            if not playlist:
                return "Playlist not found:", name

            version_id = self.dialog.v_info.get('id')
            version_info = self.dialog.sg.find_one('Version', [['id', 'is', version_id]], ['playlists'])
            playlists = version_info.get('playlists')
            playlists.append(playlist)

            self.dialog.sg.update('Version', version_id, {'playlists': playlists})
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

