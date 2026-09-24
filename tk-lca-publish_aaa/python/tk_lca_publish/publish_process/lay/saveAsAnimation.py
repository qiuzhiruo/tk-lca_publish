# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import os
import traceback
import shutil
import pymel.core as pm
import maya.cmds as cmds

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将Layout文件另存为animation task文件夹下，并重命名。"
        self.description = u"将Layout文件另存为animation task文件夹下，并重命名。如果引用了layout rigging资产，则替换。"
        return

    def saveAs(self):
        #save as to animation task folder
        ani_task = os.path.dirname(pm.sceneName()).replace('\\', '/').replace('/lay/', '/ani/')
        if not ani_task.endswith('/'):
            ani_task = ani_task + '/'

        if not os.path.isdir( ani_task ):
            print 'Save As Animation: failed to find task directory of animation, canceled copying of animation file from layout'
            return ''

        # save as v000 version
        ani_file = self.dialog.entity['name'] + '.ani.animation.v000.ma'

        if os.path.isfile( ani_task+self.dialog.entity['name'] + '.ani.animation.v001.ma' ):
            # we don't overwrite animation file if v001 exists
            print 'Save As Animation: The first version of animation file exists, canceled copying of animation file from layout'
            return ''

        # do we have write permission?
        if not os.access(ani_task, os.W_OK):
            print 'Save As Animation: You do not have permission to write the directory ' + ani_task
            return ''

        # now we copy layout file to animation, rename, and replace layout.rigging to rig.rigging
        lay_task = os.path.dirname(pm.sceneName()).replace('\\', '/')
        if not lay_task.endswith('/'):
            lay_task = lay_task + '/'

        try:
            # copy and rename, in the layout folder, we will move it to animation folder later
            shutil.copyfile( pm.sceneName().replace('\\', '/'), lay_task+ani_file )
        except:
            print traceback.format_exc()
            print 'Save As Animation: You probably do not have permission to overwrite the existing animation file'
            return ''

        try:
            # read content
            f = open( lay_task+ani_file, 'r' )
            contents = f.read()
            f.close()
        except:
            print traceback.format_exc()
            print 'Save As Animation: failed to read ' + lay_task+ani_file
            try:
                os.remove( lay_task+ani_file )
            except:
                pass
            return ''

        try:
            # replace
            contents = contents.split('\n')
            new_contents = []
            for line in contents:
                if '.rig.layout_rigging' in line:
                    path = line.split('"')
                    for p in path:
                        if '.rig.layout_rigging' in p:
                            p = p.replace('.rig.layout_rigging', '.rig.rigging').replace('\\', '/')
                            if os.name == 'posix':
                                p = p.replace('Z:', '/mnt/proj')
                            else:
                                p = p.replace('/mnt/proj', 'Z:')
                            if os.path.isfile(p):
                                line = line.replace('.rig.layout_rigging', '.rig.rigging')
                            break
                new_contents.append( line )
            f = open( lay_task+ani_file, 'w')
            f.write( '\n'.join(new_contents) )
            f.close()
        except:
            print traceback.format_exc()
            print 'Save As Animation: failed to replace layout_rigging for ' + lay_task+ani_file
            try:
                os.remove( lay_task+ani_file )
            except:
                pass
            return ''

        try:
            # move the animation
            shutil.copyfile( lay_task+ani_file, ani_task+ani_file )
            os.remove( lay_task+ani_file )
        except:
            print traceback.format_exc()

        # we also copy particle cache if any
        try:
            if os.path.isdir(lay_task+'particles'):
                # remove paritcles directory in ani task folder
                shutil.rmtree( ani_task+'particles' )
                # do the copy stuff
                shutil.copytree( lay_task+'particles', ani_task+'particles' )
        except:
            print traceback.format_exc()

        return ''

    def proceed(self):
        try:
            self.saveAs()
            return ""
        except:
            return traceback.format_exc()
            return ""


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
