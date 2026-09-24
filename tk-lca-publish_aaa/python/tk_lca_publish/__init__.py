# -*- coding:utf-8 -*-

"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

"""
import os
import sys

sys.path.append(os.path.split( __file__ )[0])

# sys.path.append("U:/toolset/lib/production")
# sys.path.append("/mnt/utility/toolset/lib/production")
# sys.path.append("/Volumes/utility/toolset/lib/production")
#
# sys.path.append("Z:/software/pyside/pyside111_py26_qt471_win64/python")
# sys.path.append("/mnt/proj/software/pyside/pyside112_py26_qt471_linux/python")
# sys.path.append("/Volumes/lcadata/software/pyside/pyside112_py26_qt471_mac/python")

#os.environ['LD_LIBRARY_PATH'] = '/usr/autodesk/maya2013-x64/lib:/opt/chromium:/opt/chromium/lib:/opt/chromium/lib.target'
# from PySide import QtGui
import sgtk
import tank
try:
    from sgtk.platform.qt import QtCore, QtGui

except Exception as e:
    pass


def launch_app(app, proj, step, step_description):
    if os.path.isdir(os.path.dirname(__file__) + '/depts/' + proj['name'].lower() + '/' + step):
        step_module = 'depts.%s.%s.app_dialog' % (proj['name'].lower(), step)
    else:
        step_module = 'depts.default.%s.app_dialog' % step

    # defer imports so that the app works gracefully in batch modes
    app_dialog = __import__(step_module, globals(), fromlist=[''], level=1)
    # show the dialog window using the engine's show_dialog method
    app.engine.show_dialog(step_description + " Publish", app, app_dialog.AppDialog, app)
    return


def show_dialog(app):

    ctx = app.context
    proj = ctx.project
    entity = app.shotgun.find_one(ctx.entity['type'], [['id', 'is', ctx.entity['id']]], ['type', 'sg_asset_type', 'code'])
    task = ctx.task
    step = ctx.step
    engine_name = app.engine._Engine__engine_instance_name

    '''try:
        app.log_debug("Creating folders for %s %s" % (entity['type'], entity['id']))
        app.tank.create_filesystem_structure(entity['type'], entity['id'])
    except tank.TankError, err:
        raise tank.TankError("Could not create folders on disk. Error reported: %s" % err)'''

    if step['name'] == 'doc' :
        launch_app(app, proj, 'doc', "DOCUMENT")

    elif step['name'] == 'art':
        if entity['type'] == 'Shot':
            launch_app(app, proj, 'art_shot', "ART Shot")
        else:
            launch_app(app, proj, 'art', "ART")

    elif  step['name'] == 'aud':
        launch_app(app, proj, 'aud', "AUD")

    elif  step['name'] == 'edt':
        if task['name'] != 'picture_lock':
            launch_app(app, proj, 'edt', "EDT")
        else:
            if sys.platform.startswith('linux'):
                launch_app(app, proj, 'picture_lock', "Picture Lock")
            else:
                msgBox = QtGui.QMessageBox()
                msgBox.setText(u"Picture Lock Publish 必须在 Linux 下运行。" )
                msgBox.exec_()

    elif  step['name'] == 'stb':
        launch_app(app, proj, 'stb', "STB")

    elif  step['name'] == 'mod':
        if engine_name == 'tk-maya':
            print 'entity : ',entity
            print 'task : ',task
            
            if entity['sg_asset_type']=='asb':
                if task['name'].startswith('assembly'):
                    launch_app(app, proj, 'mod_assembly', "Sub Assets")
                else:
                    launch_app(app, proj, 'mod_asb', "ASB MOD")

            elif entity['sg_asset_type']=='scn':
                launch_app(app, proj, 'scn', "SCN")
            elif entity['sg_asset_type']=='asm':
                launch_app(app, proj, 'mod_asm', "ASM")
            else:
                if task['name'] == "model_lite":
                    launch_app(app, proj, 'mod_lite', "MOD")
                else:
                    launch_app(app, proj, 'mod', "MOD")

        elif engine_name == 'tk-shotgun':
            if entity['sg_asset_type']=='asb' and task['name'] == 'model':
                launch_app(app, proj, 'hyperloop', "Hyper Loop")

        elif task['name'] == 'dynamic':
            launch_app(app, proj, 'mod_dynamic', "Dynamic MOD")
        else:
            launch_app(app, proj, 'mod', "MOD")

    elif  step['name'] == 'rig':
        if engine_name == 'tk-maya':
            if task['name'] == 'rigging_layout' or task['name'] == 'layout_rig':
                if entity['sg_asset_type'] in ['chr', 'rra','crd', 'asb', 'prp','veh']:
                    launch_app(app, proj, 'rig_lay', "LAY RIG")
                elif entity['sg_asset_type'] =='asm':
                    launch_app(app, proj, 'rig_asm_lay', "ASM LAY RIG")
                else:
                    QtGui.QMessageBox.information(None, u'无法打开publish窗口', u'资产类rigging_layout任务只能publish chr/crd/asb类的资产')

            elif task['name'] == 'rigging_blocking':
                launch_app(app, proj, 'rig_block', "BLOCK RIG")

            elif task['name'] == 'rigging_ani':
                launch_app(app, proj, 'rig_ani', "ANI RIG")
            elif entity['sg_asset_type']=='asm' and task['name'] == 'rigging_body':
                launch_app(app, proj, 'rig_asm', "ASM RIG")
            elif entity['sg_asset_type']=='asm' and task['name'] == 'rigging_facial':
                launch_app(app, proj, 'rig_asm', "ASM RIG")

            elif task['name'] == 'rigging_body':
                launch_app(app, proj, 'rig_body', "RIG BODY")
            elif task['name'] == 'rigging_facial':
                launch_app(app, proj, 'rig_facial', "RIG FACIAL")
            elif entity['sg_asset_type']=='asb':
                launch_app(app, proj, 'rig_asb', "ASB RIG")
            elif entity['sg_asset_type']=='asm':
                launch_app(app, proj, 'rig_asm', "ASM RIG")
            elif entity['sg_asset_type']=='rra':
                launch_app(app, proj, 'rig_rra', "RRA RIG")
            elif entity['sg_asset_type']=='crd':
                launch_app(app, proj, 'rig_crd', "CRD RIG")
            else:
                launch_app(app, proj, 'rig', "RIG")
        else:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(u"Rig Publish必须在Maya内启动运行。" )
            msgBox.exec_()

    elif  step['name'] == 'srf':

        if engine_name == 'tk-katana':
            if entity['sg_asset_type']=='asb' or entity['sg_asset_type']=='scn':
                launch_app(app, proj, 'srf_asb', "Srf Asb & Scn")
            else:
                launch_app(app, proj, 'srf', "SRF")
        else:
            if entity['sg_asset_type']=='asb' or entity['sg_asset_type']=='scn':
                launch_app(app, proj, 'srf_asb', "Srf Asb & Scn")
            else:
                if task['name'] == 'uv':
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText(u"UV任务只是给PC记录UV进行状态用的，不应该在这个任务下PA东西。如果要Publish，可以在同一个资产的 surfacing 任务下 PA" )
                    msgBox.exec_()
                else:
                    launch_app(app, proj, 'srf_sg', "Srf SG")

    elif step['name'] == 'set':
        launch_app(app, proj, 'set', "SET")

    elif step['name'] == 'lay':
        if entity['type'] == 'Sequence':
            launch_app(app, proj, 'lay_sequence', "LAY Sequence")
        else:
            launch_app(app, proj, 'lay', "LAY")

    elif step['name'] == 'flo':
        if task['name'] == 'final_layout':
            launch_app(app, proj, 'flo', "FLO")
        elif task['name'] == 'stereo':
            launch_app(app, proj, 'stereo', "Stereo")

    elif  step['name'] == 'ani':
        if task['name'] == 'reference':
            launch_app(app, proj, 'ani_ref', "ANI Reference")
        elif task['name'] == 'animation':
            launch_app(app, proj, 'ani', "ANI")
        elif entity['sg_asset_type'] in ['crd', 'chr','oat']:
            launch_app(app, proj, 'ani_crowd', "Crowd Action")
        else:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(u"不可以从%s任务Publish文件。"%task['name'])
            msgBox.exec_()

    elif step['name'] == 'crd':
        if entity['type'] == 'Asset':
            if engine_name == 'tk-maya':
                if entity['sg_asset_type'] == 'oat':
                    launch_app(app, proj, 'crd_oat', "CRD OAT")
                else:
                    launch_app(app, proj, 'crd_asset', "Crowd Asset")
            else:
                msgBox = QtGui.QMessageBox()
                msgBox.setText(u"Crowd Publish必须在Maya内启动运行。" )
                msgBox.exec_()
        else:
            # TODO: crowd shot publish
            launch_app(app, proj, 'crd_shot', "Crowd Shot")
            pass

    elif step['name'] == 'cfx' and entity['type'] == 'Asset':
        launch_app(app, proj, 'cfx_asset', "CFX Asset")
    elif step['name'] == 'cfx' and entity['type'] == 'Shot':
        launch_app(app, proj, 'cfx_shot', "CFX Shot")
    elif step['name'] == 'plt':
        if task['name']!='plant_edit':
            if  engine_name == 'tk-maya': 
                if entity['type'] == 'Shot':
                    launch_app(app, proj, 'plt_shot', "PLT Shot")
                elif  entity['type'] == 'Asset':
                    launch_app(app, proj, 'plt', "Plant Asset")
            else:
                launch_app(app, proj, 'plt_sg', "Plant Shotgun")
        else:
            launch_app(app, proj, 'gen', "General Daily")

    elif step['name'] == 'cty' :#and entity['type'] == 'Asset':
        launch_app(app, proj, 'cty', "City")
    elif step['name'] == 'efx':
        launch_app(app, proj, 'efx_asset', "EFX")

    elif step['name'] == 'dmt' and entity['type'] == 'Asset':
        if engine_name == 'tk-nuke':
            launch_app(app, proj, 'dmt_asset', "DMT Asset")
        else:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(u"DMT Publish必须在Nuke内启动运行。" )
            msgBox.exec_()

    elif step['name'] == 'dmt' and entity['type'] == 'Shot':
        if engine_name == 'tk-nuke':
            launch_app(app, proj, 'dmt', "DMT Shot")
        else:
            msgBox = QtGui.QMessageBox()
            msgBox.setText(u"DMT Publish必须在Nuke内启动运行。" )
            msgBox.exec_()

    elif  step['name'] == 'lgt':
        if entity['type'] == 'Shot':
            launch_app(app, proj, 'lgt', "LGT")
        elif entity['type'] == 'Sequence':
            launch_app(app, proj, 'lgt_rig', "LGT Rig")

    elif step['name'] == 'pfx' :
        if task['name'] == 'paint_fix':
            launch_app(app, proj, 'pfx', "Panit Fix")
        elif task['name'] == 'floating_window':
            launch_app(app, proj, 'pfx_fw', "Floating Window")

    else:
        #finally we use a general daily publish window for those whose publish tool is not implemented.
        launch_app(app, proj, 'gen', "General Daily")
        



