# -*- coding:utf-8 -*-

import os
import traceback


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将master移动到世界坐标。"
        self.description = u"将master移动到世界坐标。并锁定。"
        return

    def proceed(self):
        try:
            import pymel.core as pm
            master = pm.PyNode('|master')
            if master.hasAttr('blendWorldPC'):
                master.setAttr('blendWorldPC', 1)



            #lock position_in_world

            WP_ATTRS=['nodeState','interpType','position_in_worldW0']
            TR_ATTRS=['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ','visibility']

            if pm.objExists('|master|world_PC'):
                world_PC = pm.PyNode('|master|world_PC')
                pm.lockNode(world_PC,lock=0)
                for attr in WP_ATTRS:
                    pm.setAttr(world_PC+'.'+attr,l=True)
                pm.lockNode(world_PC,lock=1)

            if pm.objExists('position_in_world'):
                position_in_world = pm.PyNode('position_in_world')
                pm.lockNode(world_PC,lock=0)
                for attr in TR_ATTRS:
                    pm.setAttr(position_in_world+'.'+attr,l=True)
                pm.lockNode(world_PC,lock=1)
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description



