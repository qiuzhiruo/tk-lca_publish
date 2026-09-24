# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.06
#
# Description:
#
############################################

import traceback
import time
import os


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"发送锁版本信号"
        self.description = u"各种publish后的处理:给服务器发送锁版本文件夹信号。"
        return

    def proceed(self):
        server = self.dialog.version_dir.split('projects')[0]
        try:
            server = self.dialog.version_dir.split('projects')[0]
            self.write_version_cache(server)
            # Send a singal to lock the version folder
            #server = self.dialog.version_dir.split('projects')[0]
            linux_version_dir = self.dialog.version_dir.replace(server, '/mnt/proj/')
            v_file = server + 'trash/versions/' + self.dialog.version_name + '.txt'
            with open(v_file, 'w') as f:
                f.write(linux_version_dir)

            for data in self.dialog.shots_preview_data:
                linux_version_dir = data['version_dir'].replace('\\', '/').replace(server, '/mnt/proj/')
                v_file = server + 'trash/versions/' + data['version_name'] + '.txt'
                with open(v_file, 'w') as f:
                    f.write(linux_version_dir)

            # Recode sequence name into Sunburn queue.
            try:
                with open(server + 'trash/sunburn/queue', 'a') as f:
                    f.write('%s %s\n' % (self.dialog.project['name'].lower(),
                                         self.dialog.version_name.split('.')[0]))
            except:
                pass
            #test
            # Record preview paths in cache file

            # version_cache = server + 'trash/log/1984/Version_Caches/' + self.dialog.project['name'].lower() + '.txt'
            # if os.path.isfile(version_cache):
            #     with open(version_cache, 'a') as f:
            #         for data in self.dialog.shots_preview_data:
            #             f.write(data['version_preview'].replace('\\', '/').replace(server, '/mnt/proj/')+'\n')

            # Time cost
            self.dialog.sg.update('Version',
                                  self.dialog.v_info['id'],
                                  {'sg_publish_time':int(time.time()-self.dialog.start_time)})

            return ""
        except:
            return traceback.format_exc()

    def write_version_cache(self, server):
        version_cache = server.replace('\\', '/') + 'trash/log/1984/Version_Caches/{}.txt'.format(self.dialog.project['name'].lower())
        if os.path.isfile(version_cache):
            with open(version_cache, 'a') as f:
                for data in self.dialog.shots_preview_data:
                    f.write(data['version_preview'].replace(server, '/mnt/proj/') + '\n')
    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
