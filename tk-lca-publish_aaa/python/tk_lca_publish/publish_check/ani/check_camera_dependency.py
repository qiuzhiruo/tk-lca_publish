# -*- coding:utf-8 -*-

import traceback
import pymel.core as pm
import maya.cmds as cmds

from proc import check_camera_constraints
reload(check_camera_constraints)
import lay.lca_camera_lock.functions as functions_cl
reload(functions_cl)

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查摄像机是否只受camera rig约束"
        self.description = u"摄像机应该只受camera rig约束，如有其他约束，则应当删除。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def get_dependency_attr(self):
        cameras_grp = functions_cl.get_cameras_group()
        camera_nodes = cameras_grp.getChildren(allDescendents=True, type='transform')
        camera_nodes.append(cameras_grp)
        constraint_nodes = []
        blend_nodes =[]
        
        attrs =[]
        for node in camera_nodes:
            for attr in ('tx','ty','tz', 'rx', 'ry','rz', 's'):
                cattr = node.attr(attr)
                blends = cmds.listConnections(cattr.name(), d=0, s=1,type ='pairBlend')
                constraints = cmds.listConnections(cattr.name(), d=0, s=1,type ='constraint')  
                constraints_clean =[]                                                          
                if constraints:
                    for const in constraints: 
                        inputs = cmds.listConnections(const, d=0, s=1,type ='transform')
                        for input in inputs:
                            if input not in camera_nodes:
                                constraints_clean.append(const)
                                constraint_nodes.append(str(const))
                if blends:
                    blend_nodes.extend(blends)
                if constraints_clean or blends:
                    attrs.append(cattr)
          
                    

        constraint_nodes = list(set(constraint_nodes))
        blend_nodes = list(set(blend_nodes))
        print 'constraint_nodes',constraint_nodes
        print 'blend_nodes',blend_nodes
        print 'attrs',attrs
        return attrs,constraint_nodes,blend_nodes

    def run_check(self):
        try:
            if functions_cl.is_camera_locked():
                return ''

            self.dialog.no_cam_rig = False
            attrs,constraint_nodes,blend_nodes = self.get_dependency_attr()
            shot = self.dialog.entity.get('name')

            if self.dialog.project['name'].lower() != 'yzc':
                if constraint_nodes:
                    print constraint_nodes
                    cam_pc = '{}_cam_pointConstraint1'.format(shot)
                    cam_oc = '{}_cam_orientConstraint1'.format(shot)
                    if cam_oc not in constraint_nodes or cam_pc not in constraint_nodes:
                        return u'摄像机被camera rig以外的物体约束或摄像机的camera rig约束丢失，请检查文件，有问题请通知TD'

                    cons_tras = cmds.listConnections('{}.target'.format(cam_pc), d=False, s=True, type='transform')
                    cons_tras.remove(cam_pc)
                    cam_rig_ns = cons_tras[0].split(':')[0]
                    if cam_rig_ns != '{}_cam_rig'.format(shot):
                        return u'约束相机的rig的命名空间并非但前镜头: "{}", 请联系TD'.format(cam_rig_ns)
                else:
                    if shot[:1] in ['z']:
                        self.dialog.no_cam_rig = True
                    else:
                        return u'摄像机rig丢失，请检查文件，有问题请通知TD'
            else:
                if attrs:
                    nodes_str = '\n'.join(i.name() for i in attrs)
                    return u'摄像机以下属性依赖于场景物体，需要Bake后提交:\n%s'%nodes_str
            print 'self.dialog.no_cam_rig', self.dialog.no_cam_rig
            return ''
        except:
            return traceback.format_exc()

    def unlockTransform(self, obj):
        if isinstance(obj, pm.nodetypes.Transform):
            obj.translate.unlock()
            obj.rotate.unlock()
            obj.scale.unlock()

    def lockTransform(self, obj):
        if isinstance(obj, pm.nodetypes.Transform):
            obj.translate.lock()
            obj.rotate.lock()
            obj.scale.lock()

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
