# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import os
import traceback
import pymel.core as pm
import math
from proc import check_lay_camera

import lay.utilities.read_config_funcs as rcf; reload(rcf)
import lay.lca_camera_lock as cl;reload(cl);

IGNORED_LIST = ['z', ]
IGNORED_PROJ = ['TAP']


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"摄像机检查"
        self.description = u"检查相机根组cameras是否锁定，相机命名是否规范，相机位移是否正确，Film Aspect Ratio是否为项目标准数值"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        self.wrong_cameras_pos = False
        if self.dialog.step['name'] == 'ani':
            self.auto_fix = False
        return

    def lockTransform(self, obj):
        if isinstance(obj, pm.nodetypes.Transform):
            obj.translate.lock()
            obj.rotate.lock()
            obj.scale.lock()

    def run_check(self):
        try:
            try:
                camerasGrp = pm.PyNode('|cameras')
            except:
                return u"找不到名为 cameras 的组！"

            # cameras has to be a transform type
            if not isinstance( camerasGrp, pm.nodetypes.Transform ):
                return u"根组 cameras 必须是组，不可以是其他物体类型"
            
            sg_pivot = self.dialog.sg.find_one('Shot', [['project',  'is', self.dialog.project], ['code', 'is', self.dialog.entity['name']]], 
                                               ['sg_stage_pivot'])['sg_stage_pivot']
            
            # z1* 场次 |cameras 需要 为 0 0 0
            if self.dialog.step['name'] == 'ani' and self.dialog.entity['name'].startswith('z1'):
                if camerasGrp.getTranslation()[0] != 0.0 or camerasGrp.getTranslation()[1] != 0.0 or camerasGrp.getTranslation()[2] != 0.0:
                    if camerasGrp.isReferenced():
                        self.dialog.locked_cam_trans = camerasGrp.getTranslation()
                        print self.dialog.locked_cam_trans
                        cl.ani_unlock_camera2()
                        camerasGrp = pm.PyNode('|cameras')
                        
                    # camerasGrp = pm.PyNode('|cameras')
                    pm.lockNode(camerasGrp, lock=False)
                    pm.setAttr('{}.translate'.format(camerasGrp), lock=0)
                    for k, v in [('{}.tx'.format(camerasGrp), 0),
                                ('{}.ty'.format(camerasGrp), 0),
                                ('{}.tz'.format(camerasGrp), 0)]:
                        pm.setAttr(k, lock=0)
                        pm.setAttr(k, v)
                    pm.setAttr('{}.translate'.format(camerasGrp), lock=1)
                    pm.lockNode(camerasGrp, lock=True)
                    self.dialog.unlocked_cam_trans = camerasGrp.getTranslation()
            else:
                if sg_pivot is None:
                    # check identity
                    if self.dialog.project['name'].upper() == 'CAT':
                        self.special_shot_info = rcf.read_cat_shift_shot_config()
                        if self.dialog.entity['name'] in self.special_shot_info.keys() and \
                        not camerasGrp.getTranslation().isEquivalent(pm.dt.Vector(self.special_shot_info[self.dialog.entity['name']])):
                            self.wrong_cameras_pos = True
                            return u'%s的 cameras 位移应该为%s' % (self.dialog.entity['name'][:3], str(self.special_shot_info[self.dialog.entity['name']]))
                    else:
                        if not camerasGrp.getTransformation().isEquivalent( pm.dt.TransformationMatrix.identity ):
                            if not camerasGrp.getScale() == [10, 10, 10]:
                                return u"根组|cameras 的 translate 和 rotate 数值不为0，scale数值不为1或10"
                else:
                    assets_trans_str = sg_pivot['name'].split(' ')
                    assets_trans_floats = [-float(value) for value in assets_trans_str]
                    trans_value_vector = pm.dt.Vector(assets_trans_floats[0], assets_trans_floats[1], assets_trans_floats[2])
                    if not camerasGrp.getTranslation().isEquivalent(trans_value_vector):
                        if self.dialog.step['name'] == 'ani':
                            pm.lockNode(camerasGrp, lock=False)
                            pm.setAttr('{}.translate'.format(camerasGrp), lock=0)
                            for k, v in [('{}.tx'.format(camerasGrp), assets_trans_floats[0]),
                                        ('{}.ty'.format(camerasGrp), assets_trans_floats[1]),
                                        ('{}.tz'.format(camerasGrp), assets_trans_floats[2])]:
                                pm.setAttr(k, lock=0)
                                pm.setAttr(k, v)
                            pm.setAttr('{}.translate'.format(camerasGrp), lock=1)
                            pm.lockNode(camerasGrp, lock=True)
                            print '[PUB CHECK]: Auto Fix Camera Pos!'
                        else:
                            return u'%s的 cameras 位移应该为%s' % (self.dialog.entity['name'], str(assets_trans_floats))

            # lock attributes
            try:
                self.lockTransform( camerasGrp )
            except:
                print traceback.format_exc()

            entity_name = self.dialog.entity.get('name')
            camera = sorted( [elem.getParent() for elem in pm.listRelatives('|cameras', ad=True, pa=True, type='camera') if not isinstance(elem, pm.nodetypes.StereoRigCamera) and 'left' not in elem.name().lower() and 'right' not in elem.name().lower() and 'stereo' not in elem.name().lower() ] )
            stereoCam = [c.getParent() for c in pm.listRelatives('|cameras', ad=True, pa=True, type='stereoRigCamera')]
            if len(camera)>1:
                return u"|cameras组下只能有一个主相机"
            if len(stereoCam)>3:
                return u"|cameras组下最多只能有三组立体相机"

            # camera has to be under camera group at top level
            for cam in camera:
                if cam.getParent() != camerasGrp:
                    return str(cam) + u" 必须在cameras组下且位于第一层级，不能位于其他组或摄像机之下。"

            # check naming rule
            for cam in camera:
                if cam.name().split('|')[-1] != entity_name+'_cam':
                    return u"主相机命名不规范，应该是: " + entity_name + u'_cam'
            for cam in stereoCam:
                if not cam.name().split('|')[-1] in [entity_name+'_cam_stereoCamera', entity_name+'_cam_stereoCamera_Near', entity_name+'_cam_stereoCamera_Far']:
                    return u"立体摄像机命名不规范，应该是: " + entity_name+u'_cam_stereoCamera ' + entity_name+u'_cam_stereoCamera_Near ' + entity_name+ u'_cam_stereoCamera_Far'

            # check scale of cameras
            for cam in camera + stereoCam:
                val = cam.getScale()
                if math.fabs(val[0]-1.0) < 0.001 and math.fabs(val[1]-1.0) < 0.001 and math.fabs(val[2]-1.0) < 0.001:
                    try:
                        cam.scaleX.unlock()
                        cam.scaleY.unlock()
                        cam.scaleZ.unlock()
                        cam.scale.set(1,1,1)
                    except:
                        pass
                else:
                    return u"摄像机有缩放"

            # recover scale of left and right cameras
            for cam in stereoCam:
                leftRightCams = [c for c in pm.listRelatives(cam, c=True, pa=True, type='transform') if 'left' in c.name().lower() or 'right' in c.name().lower()]
                for lr in leftRightCams:
                    try:
                        lr.scaleX.unlock()
                        lr.scaleY.unlock()
                        lr.scaleZ.unlock()
                        lr.scale.set(1,1,1)
                    except:
                        pass
                    try:
                        lr.scaleX.lock()
                        lr.scaleY.lock()
                        lr.scaleZ.lock()
                    except:
                        pass

            # check pivot
            for cam in camera + stereoCam:
                if not all([t.isEquivalent(pm.dt.Vector.zero) for t in cam.getPivots(objectSpace=True)]):
                    # if non zero local pivots founded
                    return (str(cam)+u" 的轴心点local坐标不为0，这会影响到立体镜头的组装。可以选中该相机，使用mel命令：'xform -zeroTransformPivots;'将轴心点归为0")
            #    else:
            #        self.lockTransform( cam )

            for cam in camera:
                try:
                    self.lockTransform(cam)
                    # lock pivot
                    if self.dialog.step['name'] == 'ani':
                        cam.attr('rp').lock()
                        cam.attr('rpt').lock()
                        cam.attr('sp').lock()
                        cam.attr('spt').lock()
                        cam.attr('ra').lock()
                except:
                    print traceback.format_exc()

            shot = self.dialog.entity.get('name')
            
            if self.dialog.project['name'].upper() in IGNORED_PROJ:
                return check_lay_camera.check_test_seq_aperture(camera, self.dialog.project['name'].lower(), shot)
            
            #IGNORED_LIST is special, if 
            if any(shot.startswith(i) for i in IGNORED_LIST):
                # if has any incorrect camera, return error message string; else, return empty string
                return check_lay_camera.check_test_seq_aperture(camera, self.dialog.project['name'].lower(), shot)
            
            # check film aspect ratio
            for cam in [c.getShape() for c in camera]:
                if abs(cam.attr('horizontalFilmAperture').get() / cam.attr('verticalFilmAperture').get() - 2.386946387 ) > 0.01:
                    return (str(cam)+u" 的Film Aspect Ratios数值不为2.387。注意更改这个数值会影响angle of view，因此在创建摄像机的时候就应该改为正确的比例")
                #if abs(cam.attr('horizontalFilmAperture').get() / cam.attr('verticalFilmAperture').get() - 1.85 ) > 0.01:
                #    return (str(cam)+u" 的Film Aspect Ratios数值不为1.85。注意更改这个数值会影响angle of view，因此在创建摄像机的时候就应该改为正确的比例")
                try:
                    cam.attr('horizontalFilmAperture').lock()
                    cam.attr('verticalFilmAperture').lock()
                    cam.attr('focalLength').lock()
                except:
                    print traceback.format_exc()
                    
            #check_result_str = check_lay_camera.check_normal_abs_aperture(camera)
            #if check_result_str:
            #    return check_result_str

            # stereo camera has to be under camera group at top level
            # stereo camera has to be off-axis mode
            for cam in [c.getShape() for c in stereoCam]:
                try:
                    if not cam.isReferenced():
                        cam.setAttr('stereo', lock=False)
                    cam.attr('stereo').set(2)
                    if cam.getParent().getParent() != camerasGrp:
                        return (str(cam)+u" 必须在cameras组下且位于第一层级，不能位于其他组或摄像机之下。")
                except:
                    print traceback.format_exc()

            # resolution gate display rule
            for cam in [c.getShape() for c in camera]:
                try:
                    cam.attr('displayFilmGate').set(0)
                    cam.attr('displayResolution').set(1)
                except:
                    print traceback.format_exc()

            # global resolution setting
            try:
                pm.PyNode('defaultResolution').attr('width').set(2048)
                pm.PyNode('defaultResolution').attr('height').set(858)
            except:
                print traceback.format_exc()

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        if self.dialog.step['name'] != 'ani':
            try:
                if self.wrong_cameras_pos:
                    trans_value = self.special_shot_info[self.dialog.entity['name']]
                    if pm.PyNode('|cameras').isReferenced():
                            pm.FileReference('|cameras').importContents()

                    pm.lockNode('cameras', lock = False)
                    pm.setAttr('cameras.translate', lock = False)
                    pm.setAttr('cameras.translateX', lock = False)
                    pm.setAttr('cameras.translateY', lock = False)
                    pm.setAttr('cameras.translateZ', lock = False)
                    pm.setAttr('cameras.translateX', trans_value[0])
                    pm.setAttr('cameras.translateY', trans_value[1])
                    pm.setAttr('cameras.translateZ', trans_value[2])
                    pm.setAttr('cameras.translateX', lock = True)
                    pm.setAttr('cameras.translateY', lock = True)
                    pm.setAttr('cameras.translateZ', lock = True)
                    pm.setAttr('cameras.translate', lock = True)
                    pm.lockNode('cameras', lock = True)
                    self.wrong_cameras_pos = False
                else:
                    cam = pm.PyNode( self.dialog.entity.get('name')+'_cam' )
                    cam.attr('horizontalFilmAperture').unlock()
                    cam.attr('verticalFilmAperture').unlock()

                    animCurveType=['animCurve', 'animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU', 'animCurveUA', 'animCurveUL', 'animCurveUT', 'animCurveUU']
                    for c in list(set(cam.attr('horizontalFilmAperture').listConnections(type=animCurveType))):
                        c.output // cam.horizontalFilmAperture

                    for c in list(set(cam.attr('verticalFilmAperture').listConnections(type=animCurveType))):
                        c.output // cam.verticalFilmAperture

                    cam.attr('horizontalFilmAperture').set(0.9691)
                    cam.attr('verticalFilmAperture').set(0.406)
            except:
                print traceback.format_exc()

        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty
