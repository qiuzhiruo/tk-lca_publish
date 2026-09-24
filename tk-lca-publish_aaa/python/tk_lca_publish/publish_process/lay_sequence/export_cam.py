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

import production.mayautils.decorators as md
import production.mayautils.animation as manim

import lay.lca_camera_loader.functions as functions;reload(functions)
import lay.lca_camera_sequencer.functions as sequenser_functions;reload(sequenser_functions)

import stereo.commonFunc as cf
reload(cf)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出相机。"
        self.description = u"将每个镜头的相机输出为一个Maya文件。"
        return

    @md.d_disableViews
    def proceed(self):
        try:
            for data in self.dialog.shots_preview_data:
                self.dialog.print_log(data['version_name'])
                if not os.path.isdir(data['version_dir'] + '/camera'):
                    os.makedirs(data['version_dir'] + '/camera')

                # Version mark
                f = open(data['version_dir'] + '/camera/info.txt', 'w' )
                f.write(data['version_name'] + '\n')
                f.close()

                # Export cameras
                shot = pm.nt.Shot(data['shot_node'])
                data['offset'] = data['cut_in'] - shot.getSequenceStartTime()
                functions.bake_cam_anim(data['camera'], bake_results=True,
                                        frame_range=(shot.getSequenceStartTime(),
                                                     shot.getSequenceEndTime()))

                objects = data['camera'].getChildren()
                objects.append(data['camera'])
                manim.extend_keyframes_for_objects(objects, slope_offset = 0.1, extend_keyframe_num = 3)
                # move camera anim curves to sg_cut_in
                print 'move camera: from', shot.getSequenceStartTime(), 'to', data['cut_in'], ', offset is', data['offset']
                sequenser_functions.move_camera(data['camera'], data['offset'])         # move camera rig
                sequenser_functions.move_anim_curves(data['camera'], data['offset'])    # move baked camera itself

                objects = data['camera'].getChildren()
                for o in objects:
                    if o.type() == 'camera':
                        continue
                    try:
                        pm.delete(o)
                    except:
                        traceback.print_exc()
                data['camera'].unlock()
                data['cam_output'] = os.path.join(
                    data['version_dir'],
                    'camera',
                    '%s_cam_anim.ma'%data['shot_info']['code']
                )
                pm.select(data['camera'])
                stereo_cam = sequenser_functions.get_stereo_camera(data['camera'])
                if stereo_cam:
                    pm.select(stereo_cam, add=True)
                if os.path.isfile(data['cam_output']):
                    os.remove(data['cam_output'])
                pm.system.exportSelected(data['cam_output'], type='mayaAscii')

                # export abc cam for mod/gas
                sequenser_functions.export_tmp_camera(os.path.dirname(data['cam_output']), self.dialog.project['name'], str(shot).replace('_shot', ''),
                                                      data['cut_in'], data['cut_out'], seq_mode = True, write_log = False)


                # move back camera anim curves to original places
                sequenser_functions.move_camera(data['camera'], -data['offset'])
                sequenser_functions.move_anim_curves(data['camera'], -data['offset'])

                # Duplicate camera folder
                data['cam_dir'] = ''
                tokens = data['version_dir'].replace('\\','/').split('/')
                if not 'shot' in tokens:
                    continue
                i = tokens.index('shot')
                cam_root = '/'.join(tokens[:i+3]) + '/cam/publish/'
                if os.path.isdir(cam_root):
                    l_versions = sorted(os.listdir(cam_root))
                    last_v = 0
                    for version in l_versions:
                        if version.startswith(data['shot_info']['code']+'.cam.camera.v') and version[-3:].isdigit():
                            last_v = int(version[-3:])

                    data['cam_dir'] = cam_root + data['shot_info']['code'] + ('.cam.camera.v%03d' % (last_v+1))
                    shutil.copytree(data['version_dir'] + '/camera', data['cam_dir'])

                # check if shot_cam has animation
                cam_root_grp = pm.PyNode('|cameras')
                cam_name = data['shot_info']['code'] + '_cam'
                cam = pm.PyNode(cam_name)
                log = ''
                cam_output_info = {}
                if not cam_output_info.has_key('animated'):
                    cam_output_info.update({'animated':False})

                if cf.isAnimated(cam, ['tx','ty','tz','rx','ry','rz','focalLength', 'focalDistance']):
                    cam_output_info['animated'] = True
                if not cam_output_info['animated']:
                    for s in pm.listRelatives(cam_root_grp, ad=True, pa=True, type=['stereoSafePlane', 'stereoConvergePlane']):
                        if cf.isAnimated(s, ['redWashPosition']):
                            cam_output_info['animated'] = True
                            break
                        if cf.isAnimated(s.getParent(), ['tz']):
                            cam_output_info['animated'] = True
                            break

                # tag on shotgun if the camera is animated
                if cam_output_info.has_key('animated'):
                    log += 'need to inform shotgun if the camera is animated or static\n'
                    info = self.dialog.sg.find_one('Shot', [['project', 'name_is', self.dialog.project['name']],
                                                            ['code', 'is', data['shot_info']['code'] ]], ['sg_cam_anim'])
                    if info:
                        if cam_output_info['animated']:
                            self.dialog.sg.update('Shot', info['id'], {'sg_cam_anim':'animated'})
                            log += 'update shotgun: camera is animated\n'
                        else:
                            self.dialog.sg.update('Shot', info['id'], {'sg_cam_anim':'static'})
                            log += 'update shotgun: camera is static\n'
                    print log

            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


