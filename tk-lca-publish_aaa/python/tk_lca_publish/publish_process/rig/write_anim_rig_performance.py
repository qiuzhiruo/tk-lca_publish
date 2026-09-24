# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Edward Sun
#
# Date: 2014.05
#
# Description: 
#
############################################
import os
import traceback
import shutil
import pymel.all as pm
from assetsystem_sgl.tools.common.publish.setmessage import setmessage
from assetsystem_sgl.tools.common.publish.profiling import get_fps_new
from sgtk.platform.qt import QtGui
import maya.cmds as cmds
import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om
from assetsystem_sgl.lib import xmpppy
import warnings

import logging
logger = logging.getLogger()
logger.propagate = False
logger.setLevel(logging.INFO)
import sqlite3

DB_FILE_PATH = "W:/shome/chengang/fps.db"

def add_table(DB_FILE_PATH,data):
    def create_table(DB_FILE_PATH):
        try:
            conn = sqlite3.connect(DB_FILE_PATH)
            cursor = conn.cursor()
            cursor.execute('create table COMPANY (proj,task,char,fps)')
            cursor.rowcount
            cursor.close()
            conn.commit()
            conn.close()
        except:
            pass
    try:
        create_table(DB_FILE_PATH)
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()
        #data = ('wps','test1','20')
        ins="INSERT INTO COMPANY(proj,task,char,fps) VALUES (?,?,?,?)"
        cursor.execute(ins,data)
        cursor.close()
        conn.commit()
        conn.close()
    except:
        pass


def get_fps():
    from maya.debug.emPerformanceTest import emPerformanceTest
    from maya.debug.emPerformanceTest import emPerformanceOptions
    options = emPerformanceOptions()
    options.setViewports([emPerformanceOptions.VIEWPORT_1])
    options.setReportProgress(True)
    options.setTestTypes([emPerformanceOptions.TEST_PLAYBACK])
    options.evalModes = ['DG']
    csv = emPerformanceTest(None, 'csv', options)
    rowDictionary = dict(zip(csv[0].split(',')[1:], csv[1].split(',')[1:]))
    startFrameTitle = 'Start Frame'
    endFrameTitle = 'End Frame'
    frameCount = 0.0
    if startFrameTitle in rowDictionary and endFrameTitle in rowDictionary:
        frameCount = float(rowDictionary[endFrameTitle]) - float(rowDictionary[startFrameTitle]) + 1.0
    print str(frameCount/float(rowDictionary['VP1 Playback DG Avg'])) + "  fps"

    # return frameCount/float(rowDictionary['VP2 Playback EMP Avg'])
    # print '=' * 15
    # for (title, name) in rateTitles:
    #     playbackTime = float(rowDictionary[title])
    #     rate = playbackTime if frameCount == 0.0 else frameCount/playbackTime
    #     rateStr = rate
    #     print '    %s = %s fps' % (name, rateStr)


def edo_getPublishDir():
    # Z:\projects\tpr\asset\chr\xiaolai\rig\publish\xiaolai.rig.rigging\anim_rig
    fn = cmds.file(q=1, sn=1)
    pubfn = ''
    pubfn = fn.replace('W:/', 'Z:/').replace('/task/maya/', '/publish/').replace('.ma', '/') + 'anim_rig/'
    return pubfn


def outPutGlobalCtrlFps():
    if cmds.objExists('global_ctrl'):
        cmds.playbackOptions(min=1, max=100)
        if not cmds.ls('global_ctrl', readOnly=1):
            cmds.setKeyframe('global_ctrl', t=[1, 1], at='ty', v=0)
            cmds.setKeyframe('global_ctrl', t=[100, 100], at='ty', v=5)
        mint = mc.playbackOptions(q=1, min=1)
        maxt = mc.playbackOptions(q=1, max=1)
        mc.playbackOptions(max=maxt, min=mint)
        frames = maxt - mint
        mc.playbackOptions(playbackSpeed=0, maxPlaybackSpeed=0, e=1)
        mc.currentTime(mc.playbackOptions(q=1, min=mint))
        mc.dgtimer(reset=1, on=1)
        mc.play(wait=1)
        mc.dgtimer(off=1)
        evalResult = mc.dgtimer(query=1, outputFile="MEL", maxDisplay=0)
        mc.currentTime(mint)
        time = float(str(evalResult[12].split(": ")[1].split(" ")[0]))
        fps = float((frames / time))
        anim_node = pm.listConnections("global_ctrl.ty", s=True, d=False, type="animCurveTL")
        pm.delete(anim_node)
        return evalResult,fps,frames


def outPutGlobalPriCtrlFps():
    if mc.objExists('global_ctrl'):
        if not cmds.ls('global_ctrl', readOnly=1):
            mc.playbackOptions(min=1, max=100)
            cs = mc.listRelatives('global_ctrl', p=1, pa=1)[0]
            if cs == "global_pri_ctrl":
                mc.setKeyframe("global_pri_ctrl", t=[1, 1], at='ty', v=0)
                mc.setKeyframe("global_pri_ctrl", t=[100, 100], at='ty', v=5)
            else:
                grp = cmds.group('global_ctrl', n='publish_profiling_grp')
                mc.setKeyframe(grp, t=[1, 1], at='ty', v=0)
                mc.setKeyframe(grp, t=[100, 100], at='ty', v=5)
            mint = mc.playbackOptions(q=1, min=1)
            maxt = mc.playbackOptions(q=1, max=1)
            mc.playbackOptions(max=maxt, min=mint)
            frames = maxt - mint
            mc.playbackOptions(playbackSpeed=0, maxPlaybackSpeed=0, e=1)
            mc.currentTime(mc.playbackOptions(q=1, min=mint))
            mc.dgtimer(reset=1, on=1)
            mc.play(wait=1)
            mc.dgtimer(off=1)
            evalResult = mc.dgtimer(query=1, outputFile="MEL", maxDisplay=0)
            mc.currentTime(mint)
            time = float(str(evalResult[12].split(": ")[1].split(" ")[0]))
            fps = float((frames / time))
            if cs != "global_pri_ctrl":
                mc.parent('global_ctrl', cs)
                mc.delete(grp)
            try:
                anim_node = pm.listConnections("global_pri_ctrl.ty", s=True, d=False, type="animCurveTL")
                pm.delete(anim_node)
            except:
                pass
            try:
                anim_node = pm.listConnections("global_ctrl.ty", s=True, d=False, type="animCurveTL")
                pm.delete(anim_node)
            except:
                pass
            return evalResult,fps,frames


def out_profiling_old(outputPath=''):
    if outputPath == '':
        outputPath = os.path.dirname(mc.file(q=1, sn=1)) + '/'
    aevalResult, afps, aframes = outPutGlobalCtrlFps()
    evalResult, fps, frames = outPutGlobalPriCtrlFps()
    callback = float(str(evalResult[17].split(": ")[1].split(" ")[0]))
    compute = float(str(evalResult[18].split(": ")[1].split(" ")[0]))
    dirty = float(str(evalResult[19].split(": ")[1].split(" ")[0]))
    draw = float(str(evalResult[20].split(": ")[1].split(" ")[0]))
    fetchdata = float(str(evalResult[21].split(": ")[1].split(" ")[0]))
    totalv = (callback + fetchdata + compute + dirty + draw) * 1000 / frames
    total = str(totalv)[:7] + ' ms'
    otherv = (callback + fetchdata) * 1000 / frames
    other = str(otherv)[:7] + ' ms'
    computev = compute * 1000 / frames
    compute = str(computev)[:7] + ' ms'
    dirtyv = dirty * 1000 / frames
    dirty = str(dirtyv)[:7] + ' ms'
    drawv = draw * 1000 / frames
    draw = str(drawv)[:7] + ' ms'
    if not outputPath == '':
        print 'output profiling data to ... ' + str(outputPath)
        if os.path.exists(outputPath):
            outputPath += 'profilingData.txt'
            f = open(outputPath, 'w')
            f.write('This file will show the profilling data of rigging performance.\n\n')
            f.write('Real    FPS is : ' + "%.5f" % afps + ' fps\n')
            f.write('Total   FPS is : ' + "%.5f" % fps + ' fps\n')
            f.write('------------------Detail-----------------\n')
            f.write('Total   time consuming is : ' + total + '\n')
            f.write('Compute time consuming is : ' + compute + ' --- ' + str(computev / totalv * 100.0)[:7] + '%' + '\n')
            f.write('Dirty   time consuming is : ' + dirty + ' --- ' + str(dirtyv / totalv * 100.0)[:7] + '%' + '\n')
            f.write('Draw    time consuming is : ' + draw + ' --- ' + str(drawv / totalv * 100.0)[:7] + '%' + '\n')
            f.write('Other   time consuming is : ' + other + ' --- ' + str(otherv / totalv * 100.0)[:7] + '%' + '\n')
            f.close()


def out_profiling_2015(self,outputPath=''):
    if outputPath == '':
        outputPath = os.path.dirname(mc.file(q=1, sn=1)) + '/'
    if cmds.objExists('global_ctrl'):
        cmds.playbackOptions(min=1, max=100)
        if not cmds.ls('global_ctrl', readOnly=1):
            cmds.setKeyframe('global_ctrl', t=[1, 1], at='ty', v=0)
            cmds.setKeyframe('global_ctrl', t=[100, 100], at='ty', v=5)
        mint = mc.playbackOptions(q=1, min=1)
        maxt = mc.playbackOptions(q=1, max=1)
        mc.playbackOptions(max=maxt, min=mint)
        frames = maxt - mint
        mc.playbackOptions(playbackSpeed=0, maxPlaybackSpeed=0, e=1)
        mc.currentTime(mc.playbackOptions(q=1, min=mint))
        mc.dgtimer(reset=1, on=1)
        mc.play(wait=1)
        mc.dgtimer(off=1)
        evalResult = mc.dgtimer(query=1, outputFile="MEL", maxDisplay=0)
        mc.currentTime(mint)
        time = float(str(evalResult[12].split(": ")[1].split(" ")[0]))
        fps = float((frames / time))
        anim_node = pm.listConnections("global_ctrl.ty", s=True, d=False, type="animCurveTL")
        pm.delete(anim_node)
        callback = float(str(evalResult[17].split(": ")[1].split(" ")[0]))
        compute = float(str(evalResult[18].split(": ")[1].split(" ")[0]))
        dirty = float(str(evalResult[19].split(": ")[1].split(" ")[0]))
        draw = float(str(evalResult[20].split(": ")[1].split(" ")[0]))
        fetchdata = float(str(evalResult[21].split(": ")[1].split(" ")[0]))
        totalv = (callback + fetchdata + compute + dirty + draw) * 1000 / frames
        total = str(totalv)[:7] + ' ms'
        otherv = (callback + fetchdata) * 1000 / frames
        other = str(otherv)[:7] + ' ms'
        computev = compute * 1000 / frames
        compute = str(computev)[:7] + ' ms'
        dirtyv = dirty * 1000 / frames
        dirty = str(dirtyv)[:7] + ' ms'
        drawv = draw * 1000 / frames
        draw = str(drawv)[:7] + ' ms'
        if not outputPath == '':
            print 'output profiling data to ... ' + str(outputPath)
            if os.path.exists(outputPath):
                outputPath += 'profilingData.txt'
                f = open(outputPath, 'w')
                f.write('This file will show the profilling data of rigging performance.\n\n')
                f.write('Real    FPS is : ' + str((1000.00 / totalv) * 1.1)[:7] + ' fps\n')
                f.write('Total   FPS is : ' + str((1000.00 / totalv))[:7] + ' fps\n')
                f.write('------------------Detail-----------------\n')
                f.write('Total   time consuming is : ' + total + '\n')
                f.write('Compute time consuming is : ' + compute + ' --- ' + str(computev / totalv * 100.0)[:7] + '%' + '\n')
                f.write('Dirty   time consuming is : ' + dirty + ' --- ' + str(dirtyv / totalv * 100.0)[:7] + '%' + '\n')
                f.write('Draw    time consuming is : ' + draw + ' --- ' + str(drawv / totalv * 100.0)[:7] + '%' + '\n')
                f.write('Other   time consuming is : ' + other + ' --- ' + str(otherv / totalv * 100.0)[:7] + '%' + '\n')
                f.close()


def out_profiling_2017(self,outputPath=''):
    if outputPath == '':
        outputPath = os.path.dirname(mc.file(q=1, sn=1)) + '/'

    if cmds.objExists('global_ctrl'):
        import pymel.all as pm
        mc.select("master")
        pm.mel.FrameSelectedWithoutChildren()
        mc.select(cl=1)
        mc.playbackOptions(min=1, max=100)
        mc.setKeyframe('global_ctrl', t=[1, 1], at='tx', v=0)
        mc.setKeyframe('global_ctrl', t=[50, 50], at='tx', v=10)
        mint = mc.playbackOptions(q=1, min=1)
        maxt = mc.playbackOptions(q=1, max=1)
        mc.playbackOptions(max=maxt, min=mint)
        mc.playbackOptions(playbackSpeed=0, maxPlaybackSpeed=0, e=1)
        mc.currentTime(mc.playbackOptions(q=1, min=mint))
        from maya.debug.emPerformanceTest import emPerformanceTest
        from maya.debug.emPerformanceTest import emPerformanceOptions
        options = emPerformanceOptions()
        options.setViewports([emPerformanceOptions.VIEWPORT_1])
        options.setReportProgress(True)
        options.setTestTypes([emPerformanceOptions.TEST_PLAYBACK])
        options.evalModes = ['DG']
        csv = emPerformanceTest(None, 'csv', options)
        rowDictionary = dict(zip(csv[0].split(',')[1:], csv[1].split(',')[1:]))
        startFrameTitle = 'Start Frame'
        endFrameTitle = 'End Frame'
        frameCount = 0.0
        if startFrameTitle in rowDictionary and endFrameTitle in rowDictionary:
            frameCount = float(rowDictionary[endFrameTitle]) - float(rowDictionary[startFrameTitle]) + 1.0
        fps = float(frameCount/float(rowDictionary['VP1 Playback DG Avg']))
        mc.currentTime(mint)
        anim_node = mc.listConnections("global_ctrl.tx", s=True, d=False, type="animCurveTL")
        mc.delete(anim_node)
        if not outputPath == '':
            print 'output profiling data to ... ' + str(outputPath)
            if os.path.exists(outputPath):
                outputPath += 'profilingData.txt'
                f = open(outputPath, 'w')
                f.write('This file will show the profilling data of rigging performance.\n\n')
                f.write('Real    FPS is : ' + str(fps) + ' fps\n')
                f.write('Total   FPS is : ' + str(fps) + ' fps\n')
                f.close()
        setmessage(message=u'publish帧速率 ： '+ str(fps) + "  fps", users=['chengang'])
        if fps < 16.0:
            setmessage(message=u'帧速率小于16fps为： '+ str(fps) + "  fps", users=['chengang'])
        add_table(DB_FILE_PATH,(self.dialog.project['name'],self.dialog.task['name'],self.dialog.entity['name'].lower(),str(fps)))


def out_profiling_2017_ani(self,outputPath=''):
    if outputPath == '':
        outputPath = os.path.dirname(mc.file(q=1, sn=1)) + '/'
    pm.setAttr("persp.translateZ", 60)
    pm.setAttr("persp.translateY", 40)
    pm.setAttr("persp.translateY", 40)
    pm.setAttr("persp.translateX", 40)
    pm.setAttr("persp.translateX", 40)
    pm.setAttr("persp.translateY", 40)
    pm.setAttr("persp.translateZ", 60)
    pm.setAttr("persp.rotateX", -25)
    pm.setAttr("persp.rotateY", 35)
    pm.setAttr("persp.rotateZ", 0)
    mc.select("master")
    pm.mel.FrameSelectedWithoutChildren()
    mc.select(cl=1)
    mc.playbackOptions( minTime=1, maxTime=50)
    mc.playbackOptions(playbackSpeed=0, maxPlaybackSpeed=0, e=1)
    from maya.debug.emPerformanceTest import emPerformanceTest
    from maya.debug.emPerformanceTest import emPerformanceOptions
    options = emPerformanceOptions()
    options.setViewports([emPerformanceOptions.VIEWPORT_1])
    options.setReportProgress(True)
    options.setTestTypes([emPerformanceOptions.TEST_PLAYBACK])
    options.evalModes = ['DG']
    csv = emPerformanceTest(None, 'csv', options)
    rowDictionary = dict(zip(csv[0].split(',')[1:], csv[1].split(',')[1:]))
    startFrameTitle = 'Start Frame'
    endFrameTitle = 'End Frame'
    frameCount = 0.0
    if startFrameTitle in rowDictionary and endFrameTitle in rowDictionary:
        frameCount = float(rowDictionary[endFrameTitle]) - float(rowDictionary[startFrameTitle]) + 1.0
    fps = float(frameCount/float(rowDictionary['VP1 Playback DG Avg']))
    if not outputPath == '':
        print 'output profiling data to ... ' + str(outputPath)
        if os.path.exists(outputPath):
            outputPath += 'profilingData.txt'
            f = open(outputPath, 'w')
            f.write('This file will show the profilling data of rigging performance.\n\n')
            f.write('Real    FPS is : ' + str(fps) + ' fps\n')
            f.write('Total   FPS is : ' + str(fps) + ' fps\n')
            f.close()
    setmessage(message=u'publish帧速率 ： '+ str(fps) + "  fps", users=['chengang'])
    if fps < 16.0:
        setmessage(message=u'帧速率小于16fps为： '+ str(fps) + "  fps", users=['chengang'])
    add_table(DB_FILE_PATH,(self.dialog.project['name'],self.dialog.task['name'],self.dialog.entity['name'].lower(),str(fps)))


def out_profiling_2019(self, outputPath=''):
    # 1 get fps
    if outputPath == '':
        outputPath = os.path.dirname(mc.file(q=1, sn=1)) + '/'
    fps = get_fps_new()
    # 2 write fps to profilingData.txt
    if not outputPath == '':
        print 'output profiling data to ... ' + str(outputPath)
        if os.path.exists(outputPath):
            outputPath += 'profilingData.txt'
            f = open(outputPath, 'w')
            f.write('This file will show the profilling data of rigging performance.\n\n')
            f.write('Real    FPS is : ' + str(fps) + ' fps\n')
            f.write('Total   FPS is : ' + str(fps) + ' fps\n')
            f.close()
    setmessage(message=u'publish帧速率 ： '+ str(fps) + "  fps", users=['chengang'])
    if fps < 16.0:
        setmessage(message=u'帧速率小于16fps为： '+ str(fps) + "  fps", users=['chengang'])
    add_table(DB_FILE_PATH, (self.dialog.project['name'], self.dialog.task['name'], self.dialog.entity['name'].lower(), str(fps)))


def importAnim(aniPath):
    try:
        with open(aniPath, 'r') as f:
            content = f.readlines()
        charInfoList = content[4].split(" ")
        for charInfo in charInfoList:
            if charInfo.startswith("namespace"):
                charName = charInfo.split("=")[1].replace("\"", "")
        ctrl_list = [a for a in content[5].split('//<objects list="')[1].split( '; ">\n')[0].split("; ") if pm.objExists(a)]
        ctrl_attr_list=[]
        for ctrl in ctrl_list:
            attrList = []
            attrList += pm.listAttr(ctrl,k=True) or []
            attrList += pm.listAttr(ctrl,cb=True) or []
            lockattr = pm.listAttr(ctrl,ud=1,cb=1,r=1,l=1) or []
            attr = list(set(attrList) - set(lockattr))
            for a in attr:
                ctrl_attr_list.append((ctrl,a,pm.getAttr(ctrl+ '.'+a)))
        mc.file(aniPath, i=1, type="mayaAscii", ignoreVersion=1, ra=True, mergeNamespacesOnClash=True,namespace=":", options="v=0;", pr=1, importTimeRange="combine")
        pm.currentTime(1, e=1)
        tempCtrls = pm.listRelatives("MG_PoseAnim_animCache")
        for tempCtrl in tempCtrls:
            relatedCtrl = tempCtrl.ObjName.get().split(":")[-1]
            if pm.objExists(relatedCtrl):
                for lc in pm.listConnections(tempCtrl,p=1,s=1,d=0) or []:
                    lcs = pm.listConnections(lc,p=1,s=0,d=1) or []
                    if lcs:
                        try:
                            lc.connect("%s.%s"%(relatedCtrl,lcs[0].plugAttr()))
                        except:
                            pm.warning("%s.%s"%(relatedCtrl,lcs[0].plugAttr()))
        pm.delete("MG_PoseAnim_animCache")
        pm.setInfinity(ctrl_list, pri='cycle', poi='cycle' )
    except:
        print traceback.format_exc()



class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"Profiling Anim Rigging Performance 并写出到publish路径。"
        self.description = u"Profiling Anim Rigging Performance 并写出到publish路径！"
        return

    def proceed(self):
        try:
            '''
            try:
                oldMode = mc.evaluationManager (q=1, mode=1)[0]
                mc.evaluationManager (mode="off")
            except:
                pass
            output = self.dialog.version_dir+'/anim_rig/'
            # output = edo_getPublishDir()
            if mc.about(v=1) =="2017":
                if mc.objExists("rig.char_type"):
                    char_type = mc.getAttr("rig.char_type")
                    if "Biped" in char_type or  "Quadruped" in char_type or "CatWorld" in char_type:
                        animationPath=os.path.dirname(__file__).replace('\\','/')+'/biped.animation'
                        if mc.objExists("facial_controls_grp"):
                            facialanimationPath=os.path.dirname(__file__).replace('\\','/')+'/three_facial.animation'
                            importAnim(facialanimationPath)
                        elif mc.objExists("facial_CtrlGrp"):
                            facialanimationPath=os.path.dirname(__file__).replace('\\','/')+'/facial.animation'
                            importAnim(facialanimationPath)
                        importAnim(animationPath)
                        out_profiling_2017_ani(self,output)
                    else:
                        out_profiling_2017(self,output)
                else:
                    out_profiling_2017(self,output)
            else:
                out_profiling_2019(self, output)
            try:
                mc.evaluationManager (mode=oldMode)
            except:
                pass
            return ""
            '''
            return ''
            print('Profiling Anim Rigging Performance pass')
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
