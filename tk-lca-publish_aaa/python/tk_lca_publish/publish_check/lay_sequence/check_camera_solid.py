# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import os
import traceback
import pymel.core as pm
import math
from proc import check_lay_camera

IGNORED_LIST = ['z', ]          #represents test sequence


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"摄像机检查"
        self.description = u"检查相机根组cameras是否锁定，相机命名是否规范，Film Aspect Ratio是否为项目标准数值，filmFit是否为Horizontal"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            try:
                camerasGrp = pm.PyNode('|cameras')
            except:
                return u"找不到名为 cameras 的组！"

            # cameras has to be a transform type
            if not isinstance( camerasGrp, pm.nodetypes.Transform ):
                return u"根组 cameras 必须是组，不可以是其他物体类型"
            # check identity
            if not camerasGrp.getTransformation().isEquivalent( pm.dt.TransformationMatrix.identity ):
                return u"根组 cameras 的 translate 和 rotate 数值不为0，scale数值不为1"

            entity_name = self.dialog.entity.get('name')
            camera = sorted( [elem.getParent() for elem in pm.listRelatives('|cameras', ad=True, pa=True, type='camera') if not isinstance(elem, pm.nodetypes.StereoRigCamera) and 'left' not in elem.name().lower() and 'right' not in elem.name().lower() and 'stereo' not in elem.name().lower() ] )
            stereoCam = [c.getParent() for c in pm.listRelatives('|cameras', ad=True, pa=True, type='stereoRigCamera')]
            ## check naming rule
            for cam in camera + stereoCam:
                if not cam.name().startswith(entity_name):
                    return u"摄像机命名不规范"

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

            # check pivot
            for cam in camera + stereoCam:
                if not all([t.isEquivalent(pm.dt.Vector.zero) for t in cam.getPivots(objectSpace=True)]):
                    return (str(cam)+u" 的轴心点local坐标不为0，这会影响到立体镜头的组装。可以选中该相机，使用mel命令：'xform -zeroTransformPivots;'将轴心点归为0")

            #if any(entity_name.startswith(i) for i in IGNORED_LIST):
                #return ''
                
            #IGNORED_LIST is special, if 
            if any(entity_name.startswith(i) for i in IGNORED_LIST):
                # if has any incorrect camera, return error message string; else, return empty string
                return check_lay_camera.check_test_seq_aperture(camera)

            # check film aspect ratio
            for cam in [c.getShape() for c in camera]:
                if abs(cam.attr('horizontalFilmAperture').get() / cam.attr('verticalFilmAperture').get() - 2.387 ) > 0.01:
                    return (str(cam)+u" 的Film Aspect Ratios数值不为2.387。注意更改这个数值会影响angle of view，因此在创建摄像机的时候就应该改为正确的比例")
                
            #check absoluted camera aperture values, if check_result_str is not an empty string, return the checking result
            check_result_str = check_lay_camera.check_normal_abs_aperture(camera)
            if check_result_str:
                return check_result_str
            
            # stereo camera has to be under camera group at top level
            # stereo camera has to be off-axis mode
            for cam in [c.getShape() for c in stereoCam]:
                try:
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

            # Fit Resolution Gate should be "Horizontal":
            for cam in [c.getShape() for c in camera]:
                if cam.attr('filmFit').get() != 1:
                    return  (str(cam) + u".filmFit 属性应该设置为Horizontal 或1")

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
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty
