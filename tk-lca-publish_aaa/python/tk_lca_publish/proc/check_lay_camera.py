# -*- coding:utf-8 -*-

import os
import traceback
import pymel.core as pm
import production.lca_poster as lp

reload(lp)

#IGNORED_LIST = ['z', ]          #represents test sequence


def check_normal_abs_aperture(cameras):
    '''
    '''
    from lay.lca_camera_sequencer import functions
    filmback_width = functions.FILM_BACK_WIDTH
    filmback_height = functions.FILM_BACK_HEIGHT
    #standard_ratio = 2.386946387
    standard_ratio = filmback_width / filmback_height
    check_result_str = ''

    incorrect_cams = []
    for cam in [c.getShape() for c in cameras]:
        if abs( cam.attr('horizontalFilmAperture').get() / cam.attr('verticalFilmAperture').get() - standard_ratio ) > 0.01:
            incorrect_cams.append(str(cam))

    if incorrect_cams:
        check_result_str = ','.join(incorrect_cams) + \
            u'的Horizontal Film Aperture值不为0.969，或/和 Vertical Film Aperture的值不为0.406。请修改为正确的数值。'
    return check_result_str


def check_test_seq_aperture(cameras, proj=None, shot=None):
    '''
    '''
    check_result_str = ''
    # 自定义尺寸镜头, 比如海报镜头跳过此检查
    if proj and shot:
        lps_info = lp.LcaPosterSetting(proj, shot)
        shot_resolution = lps_info.shot_resolution
        if shot_resolution:
            # 海报 skip 此项检查项
            # TODO: cam的Horizontal 与 Vertical Film Aperture两个属性的比值 应该和 Render Settings->Image Size->Width和
            #  Height的比值 有所关系，修改image尺寸的时候是不是也应该修改下 Camera Aperture
            return check_result_str

    width = pm.PyNode('defaultResolution').attr('width').get()
    height = pm.PyNode('defaultResolution').attr('height').get()
    render_ratio = (width+0.0)/height
    print 'width', width, 'height', height, 'render_ratio: ', render_ratio

    incorrect_cams = []
    for cam in [c.getShape() for c in cameras]:
        cam_h_Aperture = cam.attr('horizontalFilmAperture').get()
        cam_v_Aperture = cam.attr('verticalFilmAperture').get()
        cam_ratio = cam_h_Aperture / cam_v_Aperture
        print 'cam_ratio: ', cam_ratio
        if abs(cam_ratio - render_ratio)>0.01:
            incorrect_cams.append(str(cam))

    if incorrect_cams:
        check_result_str = ','.join(incorrect_cams) + \
                           u'的Horizontal 与 Vertical Film Aperture两个属性的比值不等于Render Settings->Image Size->Width和Height的比值。请修改为正确数值。'
    return check_result_str
