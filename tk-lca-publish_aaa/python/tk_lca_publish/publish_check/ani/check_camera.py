# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'
__maintainer__ = 'zhangzheng'

import os
import traceback
import pymel.core as pm

import lay.utilities.read_config_funcs as rcf; reload(rcf)

IGNORED_LIST = ['z', ]


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"摄像机检查"
        self.description = u"检查相机根组cameras是否锁定，相机命名是否规范，相机位移是否正确，Film Aspect Ratio是否为项目标准数值"
        self.auto_fix = True
        self.duty = u"艺术家本人"
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
            if sg_pivot is None:
                # check identity
                if self.dialog.project['name'].upper() == 'CAT':
                    self.special_shot_info = rcf.read_cat_shift_shot_config()
                    if self.dialog.entity['name'] in self.special_shot_info.keys() and \
                       not camerasGrp.getTranslation().isEquivalent(pm.dt.Vector(self.special_shot_info[self.dialog.entity['name']])):
                        return u'%s的 cameras 位移应该为%s' % (self.dialog.entity['name'], str(self.special_shot_info[self.dialog.entity['name']]))
                else:            
                    if not camerasGrp.getTransformation().isEquivalent( pm.dt.TransformationMatrix.identity ):
                        if not camerasGrp.getScale() == [10,10,10]:
                            return u"根组|cameras 的 translate 和 rotate 数值不为0，scale数值不为1或10"
            else:
                assets_trans_str = sg_pivot['name'].split(' ')
                assets_trans_floats = [-float(value) for value in assets_trans_str]
                trans_value_vector = pm.dt.Vector(assets_trans_floats[0], assets_trans_floats[1], assets_trans_floats[2])
                if not camerasGrp.getTranslation().isEquivalent(trans_value_vector):
                    return u'%s的 cameras 位移应该为%s' % (self.dialog.entity['name'], str(assets_trans_floats))
                
            # lock attributes
            try:
                self.lockTransform( camerasGrp )
            except:
                print traceback.format_exc()

            camera = [c for c in pm.listRelatives('|cameras', ad=True, pa=True, type='transform') if pm.nodeType(c.getShape())=='camera' and pm.nodeType(c.getShape())!='stereoRigCamera' and pm.nodeType(c.getParent().getShape())!='stereoRigCamera']
            stereoCam = [c.getParent() for c in pm.listRelatives('|cameras', ad=True, pa=True, type='stereoRigCamera')]
            if len(camera)>1:
                return u"|cameras组下只能有一个主相机"
            # if len(stereoCam)>2:
                # return u"|cameras组下最多只能有两组立体相机"

            # check naming rule
            for cam in camera:
                scene_key = os.path.basename(pm.system.sceneName()).split('.')[0]
                if not cam.name().split('|')[-1].startswith( scene_key ):
                    return u"摄像机命名 " + cam.name().split('|')[-1] + u" 和场景名: " + scene_key + u" 不匹配。"

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
                    cam.attr('rp').lock()
                    cam.attr('rpt').lock()
                    cam.attr('sp').lock()
                    cam.attr('spt').lock()
                    cam.attr('ra').lock()
                except:
                    print traceback.format_exc()

            shot = self.dialog.entity.get('name')
            if any(shot.startswith(i) for i in IGNORED_LIST):
                return ''

            for cam in camera:
                if cam.getParent()!= camerasGrp:
                    return (str(cam)+u" 必须在cameras组下且位于第一层级，不能位于其他组或摄像机之下。")

            # check film aspect ratio

            for cam in [c.getShape() for c in camera]:
                if self.dialog.project['name'].upper() == 'CAT':
                    if abs(cam.attr('horizontalFilmAperture').get() / cam.attr('verticalFilmAperture').get() - 2.387 ) > 0.01:
                        return (str(cam)+u" 的Film Aspect Ratios数值不为2.387。注意更改这个数值会影响angle of view，因此在创建摄像机的时候就应该改为正确的比例")
                #if abs(cam.attr('horizontalFilmAperture').get() / cam.attr('verticalFilmAperture').get() - 1.85 ) > 0.01:
                #    return (str(cam)+u" 的Film Aspect Ratios数值不为1.85。注意更改这个数值会影响angle of view，因此在创建摄像机的时候就应该改为正确的比例")
                try:
                    cam.attr('horizontalFilmAperture').lock()
                    cam.attr('verticalFilmAperture').lock()
                    cam.attr('focalLength').lock()
                except:
                    print traceback.format_exc()

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
        self.dialog.print_log(u'注意！自动修复只修改cameras位置不对和用工具解锁相机添加组的情况，其他错误请艺术家自行修复')
        if self.dialog.project['name'].upper() == 'CAT' and self.dialog.entity['name'] in self.special_shot_info.keys():
            # change 'assets'
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

        camerasGrp = pm.PyNode('|cameras')
        cameras = [c for c in pm.listRelatives('|cameras', ad=True, pa=True, type='transform') if
                   pm.nodeType(c.getShape()) == 'camera' and pm.nodeType(
                       c.getShape()) != 'stereoRigCamera' and pm.nodeType(
                           c.getParent().getShape()) != 'stereoRigCamera']
        cam = cameras[0]
        add_cam_grp = ''
        f_start = pm.playbackOptions(q=True, min=True) - 3
        f_end = pm.playbackOptions(q=True, max=True) + 3

        if cam.getParent().name() == cam.name() + '_root_grp' and cam.getParent().getParent().name() == cam.name() + '_global_grp':
            add_cam_grp = cam.getParent().getParent().name()
            cam_bake_loc = pm.spaceLocator(name=cam.name() + '_bake_loc')
            pm.parent(cam_bake_loc, camerasGrp)
            cam_bake_loc.t.set(0, 0, 0)
            cam_bake_loc.r.set(0, 0, 0)
    
            pm.parentConstraint(cam, cam_bake_loc, w=True)
            pm.bakeResults(cam_bake_loc, time=(f_start, f_end))
            pm.filterCurve(cam_bake_loc)
            pm.keyTangent(cam_bake_loc,
                          inTangentType='spline',
                          outTangentType='spline')
    
            cam.t.unlock()
            cam.tx.unlock()
            cam.ty.unlock()
            cam.tz.unlock()
    
            cam.r.unlock()
            cam.rx.unlock()
            cam.ry.unlock()
            cam.rz.unlock()
    
            attrs = ['.t', '.tx', '.ty', '.tz', '.r', '.rx', '.ry', '.rz']
    
            for attr in attrs:
                if len(pm.listConnections(cam.name() + attr, s=True, d=False, c=True)) != 0:
                    attr_in = pm.connectionInfo(cam.name() + attr, sfd=True)
                    pm.disconnectAttr(attr_in, cam.name() + attr)
    
            pm.parent(cam, camerasGrp)
            bake_parnet = pm.parentConstraint(cam_bake_loc, cam, w=True)
    
            pm.bakeResults(cam, time=(f_start, f_end))
            pm.filterCurve(cam)
            pm.keyTangent(cam,
                          inTangentType='spline',
                          outTangentType='spline')
    
            cam.t.lock()
            cam.r.lock()
            pm.delete(add_cam_grp, cam_bake_loc, bake_parnet)

        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty
