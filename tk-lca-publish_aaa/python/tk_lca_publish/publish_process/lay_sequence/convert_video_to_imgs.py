# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import os
import sys
import traceback
import pprint

import pymel.core as pm

import lay.lca_trailing_effect.funcs as lte_funcs;reload(lte_funcs)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"材质球里的视频文件转为图片序列。"
        self.description = u"使用mov或avi等做特效展示的时候，farm上有些节点会读取错误，导致ani预渲染失败，因此需要转为图片序列。"
        return


    def proceed(self):
        try:
            # self.dialog.rvio_path = "C:/Program Files/Tweak/RV-4.0.10-64/bin/rvio_hw.exe"
            # self.dialog.process_shell = False
            movies = pm.ls(type = 'movie')
            for movie in movies:
                video_path = movie.fileTextureName.get()
                try:
                    imgs = video_to_imgs( self.dialog.rvio_path, self.dialog.process_shell, video_path)
                    print imgs
                except:
                    return traceback.format_exc()

                file_node, place2dtexture_node = lte_funcs.create_file_node()
                file_node.fileTextureName.set(imgs.replace('.#.', '.<f>.'))
                file_node.useFrameExtension.set(True)
                if movie.useFrameExtension.get():
                    file_node.frameOffset.set(movie.frameOffset.get())

                conns = list(set(pm.listConnections(movie.outColor, source = False, destination = True, plugs = True)))
                for conn in conns:
                    pm.disconnectAttr(conn)
                    pm.connectAttr(file_node.outColor, conn)

                place2dTextures = list(set(pm.listConnections(movie, source = True, destination = False)))
                print 'Delete: ', place2dTextures
                pm.delete(place2dTextures)
                print 'Delete: ', movie
                pm.delete(movie)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


def video_to_imgs(rvio_path, process_shell, video_path):
    video_name = os.path.basename(video_path).rsplit('.', 1)[0]
    new_dir = os.path.join(os.path.dirname(video_path), video_name).replace('\\', '/')
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    imgs_pattern = video_name + '.#.jpg'
    imgs = os.path.join(new_dir, imgs_pattern).replace('\\', '/')
    print 'img path', imgs

    cmd_str = '"' + rvio_path + '" "%s" -o "%s"' % (video_path, imgs)
    print cmd_str
    try:
        p = subprocess.Popen(cmd_str, shell = process_shell)
        out, err = p.communicate()
        if not out or len(out) == 0:
            print out
    except:
        pass

    return imgs
