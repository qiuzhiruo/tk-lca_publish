# -*- coding:utf-8 -*-

import traceback
import maya.cmds as cmds
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查animLayer"
        self.description = u"只含有一个动画层,并显示被SceneDisplayEditor隐藏的AR."
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            if self.dialog.step['name'] == 'ani':
                import ani.lca_layer_manager.scene_display_editor as lmf
                # show all objects hided by Scene Display Editor
                sdec = lmf.SceneDisplayEditorCore()
                sdec.show_all()

            # check normal anim layer
            layers = pm.ls(type='animLayer')
            if layers and len(layers) > 1:
                return u'请合并动画层'

            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        layerNames = cmds.ls(type='animLayer')
        rootLayer = cmds.animLayer(q=True, root=True)
        if layerNames:
            for layer in layerNames:
                if layer == rootLayer:
                    continue
                connected = cmds.listConnections(layer, s=1, d=0, t='transform')
                if connected:
                    objects = list(set(connected))
                    print layer, objects
                else:
                    print layer, '     no members!'
                    cmds.select(layer)
                    import lay.utilities.maya_common_ops as mco
                    reload(mco)
                    mco.set_nodes_lock_status(lock_it=False)
                    # delete empty anim layer
                    cmds.delete(layer)
                    print layer, '     has been delete!'

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

