# -*- coding:utf-8 -*-
import traceback

import pymel.core as pm


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"设置角色的Render stat属性，并提交一版预渲染"
        self.description = u"角色未勾选Render Stat的某些选项会导致下游渲染时出错，因此需要设置，自动提交预渲染以保证此版有最新预渲染"
        return

    def proceed(self):
        try:
            # incorrect render stat only appears on chr assets now, so we only check chr
            if pm.objExists('|assets|chr'):
                mesh_nodes = pm.listRelatives('|assets|chr', allDescendents=True, type='mesh')
                for mesh_node in mesh_nodes:
                    if str(mesh_node).endswith('Shape') and mesh_node.attr('visibility').get():
                        mesh_node.attr('primaryVisibility').set(True)
                        mesh_node.attr('motionBlur').set(True)
                        mesh_node.attr('receiveShadows').set(True)
                        mesh_node.attr('castsShadows').set(True)
                        mesh_node.attr('smoothShading').set(True)

            # auto submit the pre render for this shot version
            import ani.render_ani_set.submit_maya as asm
            asm.main(only_update=True, submitdl=True, use_black_back=True,render_occ=True)

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
