# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.06
#
# Description: Create tank publish file entity
#
############################################
import traceback
import sys
import os

import tank

# import getpass
# if getpass.getuser() == "haojia":
#     # import sys
#     # sys.path.append("W:/shome/tanghaojia/remote_debug/debug-eggs/pydevd-pycharm.egg_FILES/")
#     # import pydevd_pycharm
#     # import pydevd
#     # pydevd.stoptrace()
#     # pydevd_pycharm.settrace('10.0.42.9', port=6666, stdoutToServer=True, stderrToServer=True)
#     import sys
#
#     sys.path.append("/home/haojia/Work/SoftWare/pycharm-2022.1.3/debug-eggs/pydevd-pycharm.egg_FILES/")
#     import pydevd_pycharm
#     import pydevd
#
#     pydevd.stoptrace()
#     pydevd_pycharm.settrace('localhost', port=5555, stdoutToServer=True, stderrToServer=True)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun数据库为镜头建立 Published File 。"
        self.description = u"在shotgun数据库建立 PublishedFile。该entity可以被之后的流程工具引用。"
        return

    def proceed(self):
        try:
            # Check if the context is properly created
            for data in self.dialog.shots_preview_data:
                print 'data:', data
                context = tank.context.from_path(self.dialog.tk, data['version_file'])
                print 'context:', context
                print "context.entity['type']:",context.entity['type']
                if context.entity is None:
                    raise ValueError, u"路径 " + data['version_file'] + u" 无法建立有效的 context" 
                if context.entity['type'] != 'Shot':
                    raise ValueError, u"路径 " + data['version_file'] + u" 建立的 context, entity " + str(context.entity) + u" 类型不是镜头而是"+ context.entity['type']

            # Register Scene
            args = {
                "tk": self.dialog.tk,
                "comment": self.dialog.description,
                "task": self.dialog.ctx.task,
                "dependency_paths": [],
            }
            for data in self.dialog.shots_preview_data:
                thumbnail_path = os.path.join(data['version_dir'], 'preview', 'thumbnail.jpg')
                cmdStr = '"'+ self.dialog.rvio_path +'" ' + data['version_preview'] + " -o " + thumbnail_path
                os.system(cmdStr)
                if os.path.isfile(thumbnail_path):
                    args['thumbnail_path'] = thumbnail_path

                context = tank.context.from_path(self.dialog.tk, data['version_file'])
                args.update(name=os.path.splitext(data['version_name'])[0],
                            path=data['version_file'],
                            context=context,
                            task=data['task_info'],
                            version_entity=data['version_info'],
                            version_number=int(self.dialog.version_num),
                            published_file_type=self.dialog.published_file_type)
                tank.util.register_publish(**args)

                # Register Camera
                cam_publish = os.path.dirname(data['cam_dir'])
                vers = sorted(os.listdir(cam_publish))
                if vers:
                    data['cam_dir'] = os.path.join(cam_publish, vers[-1])
                cam_file = data['cam_dir'] + '/' + data['shot_info']['code'] + '_cam_anim.ma'
                if sys.platform.startswith('win'):
                    cam_file = cam_file.replace('/', '\\')

                args['published_file_type'] = 'Maya Camera'
                args["path"] = cam_file
                args["name"] = data['shot_info']['code']+'.cam.camera'
                args["version_number"] = int(data['cam_dir'][-3:])
                print 'args:'
                print args
                sg_data = tank.util.register_publish(**args)
                print 'sg_data:'
                print sg_data
                self.dialog.sg.update(sg_data['type'], sg_data['id'], {"code": os.path.basename(data['cam_dir'])+'.ma' })

            return ""

        except:
            print traceback.format_exc()
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


