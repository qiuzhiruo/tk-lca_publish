# -*- coding:utf-8 -*-
import getpass
import os
import traceback

import pymel.core as pm
import maya.cmds as cmds
import maya.api.OpenMaya as om

from proc.function_running_time import record_time


class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出一二三级角色简模"
        self.description = u"输出一二三级角色简模 to lay"
        return

    def get_bbox_center(self, obj):
        bbox = cmds.exactWorldBoundingBox(obj)

        min_x, min_y, min_z, max_x, max_y, max_z = bbox

        center = (
            (min_x + max_x) * 0.5,
            (min_y + max_y) * 0.5,
            (min_z + max_z) * 0.5
        )

        return center

    def get_bottom_x_edges(self, mesh, tolerance=0.001):
        """
        获取模型最低位置的 X方向 edge

        mesh:
            mesh名称

        return:
            edge id list
        """

        sel = om.MSelectionList()
        sel.add(mesh)

        dag = sel.getDagPath(0)

        if dag.node().hasFn(om.MFn.kTransform):
            dag.extendToShape()


        fn = om.MFnMesh(dag)

        points = fn.getPoints(
            om.MSpace.kWorld
        )


        edge_info = {}


        it = om.MItMeshEdge(dag)


        while not it.isDone():

            eid = it.index()

            v1 = it.vertexId(0)
            v2 = it.vertexId(1)


            p1 = points[v1]
            p2 = points[v2]


            dx = abs(p2.x-p1.x)
            dy = abs(p2.y-p1.y)
            dz = abs(p2.z-p1.z)


            # 判断是否为X方向edge
            if dx > dy and dx > dz:

                center_y = (
                    p1.y+p2.y
                ) * 0.5


                edge_info[eid] = center_y


            it.next()



        if not edge_info:
            return []


        # 找最低Y
        min_y = min(
            edge_info.values()
        )


        result=[]


        for eid,y in edge_info.items():

            if abs(y-min_y)<=tolerance:
                result.append(eid)


        return result[0]


    def get_high_bbox_center_object(self, objs):

        high_obj = None
        high_y = float("-inf")

        for obj in objs:

            cx, cy, cz = self.get_bbox_center(obj)

            if cy > high_y:
                high_y = cy
                high_obj = obj

        return high_obj

    @record_time(__file__)
    def proceed(self):
        for i in self.dialog.l_publish_checks:
            if 'check_polygoncruncher' == i.module_name:
                if not i.skip_checkbox.isChecked():
                    return ''
            # i.skip_checkbox.setCheckState(QtCore.Qt.Checked)

        if pm.objExists('|master|shape|to_lay'):
             # 删除多属性，不然导出选择会携带多余的mesh
            mesh_array = cmds.listRelatives('|master|shape|to_lay',type="mesh", ad=True, f=True)
            for mesh in mesh_array:
                if cmds.attributeQuery('lc_transparent', node=mesh, exists=True):
                    cmds.setAttr(mesh+'.lc_transparent',l=False)
                    cmds.deleteAttr(mesh+'.lc_transparent')
            pm.select('|master|shape|to_lay')
            if not os.path.exists(os.path.join(os.path.dirname(pm.sceneName()), 'to_lay')):
                os.mkdir(os.path.join(os.path.dirname(pm.sceneName()), 'to_lay'))

            if os.path.exists(os.path.join(os.path.dirname(pm.sceneName()), 'to_lay', os.path.basename(pm.sceneName()))):
                os.remove(os.path.join(os.path.dirname(pm.sceneName()), 'to_lay', os.path.basename(pm.sceneName())))
            pm.exportSelected(os.path.join(os.path.dirname(pm.sceneName()), 'to_lay', os.path.basename(pm.sceneName())))
            return ''

        try:
            asset = self.dialog.sg.find_one("Asset", [['project', 'is', self.dialog.project], ['code', 'is', self.dialog.entity['name']]], ['sg_diffculty2', 'sg_asset_type'])
            if asset['sg_asset_type'] != 'chr' or str(asset['sg_diffculty2']) not in  ['1', '2', '3']:
                return ''
            set_eye = False
            eyes_out = pm.ls(['R_eyeball_geoShape', 'L_eyeballs_insideShape'])
            for eye in eyes_out:
                if 'lc_transparent' in pm.listAttr(eye):
                    set_eye = True
            # 删除多属性，不然导出选择会携带多余的mesh
            mesh_array = cmds.listRelatives('|master|poly|hi|mesh_grp',type="mesh", ad=True, f=True)
            for mesh in mesh_array:
                if cmds.attributeQuery('lc_transparent', node=mesh, exists=True):
                    cmds.setAttr(mesh+'.lc_transparent',l=False)
                    cmds.deleteAttr(mesh+'.lc_transparent')

            # 如果眼球上的lc_transparent属性被直接删掉会导致眼球不透明，这里给设置为透明
            if set_eye:
                # 获取 ShadingEngine
                sge = pm.listConnections(eyes_out[0], type="shadingEngine")
                if sge:
                    # 获取材质
                    shader = pm.ls(cmds.listConnections(sge[0] + ".surfaceShader"), materials=True)
                    if shader:
                        pm.setAttr(shader[0] + ".transparency", 1, 1, 1, type="double3")
            # 复制出一份进行减面，这样不影响原有物体
            to_lay = pm.duplicate('|master|poly|hi', name='to_lay', rr=True)

            nohead_body = ''
            if str(asset['sg_diffculty2']) in ['1', '2']:
                sel = om.MSelectionList()
                sel.add(self.dialog.temp_head)
                dag = sel.getDagPath(0)
                mesh_fn = om.MFnMesh(dag)
                points = mesh_fn.getPoints(om.MSpace.kWorld)
                edge_iter = om.MItMeshEdge(dag)
                min_y = float("inf")
                min_edge_id = -1

                while not edge_iter.isDone():
                    vtx0 = edge_iter.vertexId(0)
                    vtx1 = edge_iter.vertexId(1)
                    y = (points[vtx0].y + points[vtx1].y) * 0.5
                    if y < min_y:
                        min_y = y
                        min_edge_id = edge_iter.index()
                    edge_iter.next()
                # 由于已经存在的睁眼的头与hi下面的body_geo的头颅的点序是一致的，那么先获取睁眼头的下边缘，根据这个下边缘去切割to_lay下
                # 的body_geo
                min_edge_id = self.get_bottom_x_edges(self.dialog.temp_head)
                cmds.select("{}.e[{}]".format(self.dialog.temp_head, min_edge_id))
                cmds.polySelectSp(loop=True)
                pm.mel.eval('ConvertSelectionToVertices;')
                cmds.select([i.replace(self.dialog.temp_head, '|master|poly|to_lay|mesh_grp|skin_grp|body_geo') for i in cmds.ls(sl=True)])
                pm.mel.eval('ConvertSelectionToContainedEdges;')
                cmds.polySplitEdge()
                cmds.select('|master|poly|to_lay|mesh_grp|skin_grp|body_geo')
                s_objs =  cmds.polySeparate()
                cmds.delete(ch=1)

                # 获取切下来的头并删除
                head = self.get_high_bbox_center_object(s_objs[:2])
                all_body = s_objs[:2]
                all_body.remove(head)
                nohead_body = all_body[0]
                cmds.delete(head)

            # 选择需要减面的物体进行减面
            cmds.select(cl=1)
            pm.select(pm.listRelatives(to_lay, ad=True, typ='mesh'))
            hair = ''
            face_pass_hair = ''
            if pm.objExists('|master|shape|to_cfx|hair_grp'):
                hair = pm.duplicate('|master|shape|to_cfx|hair_grp', name='hair_grp_polygon_hair', rr=True)
                pm.select(pm.listRelatives(hair, ad=True, typ='mesh'), add=True)
            if pm.objExists('|master|shape|face_pass_grp'):
                face_pass_hair = pm.duplicate('|master|shape|face_pass_grp', name='face_pass_grp_polygon_hair', rr=True)
                pm.select(pm.listRelatives(face_pass_hair, ad=True, typ='mesh'), add=True)
            if not pm.ls(typ='polygonCruncherSettingsNode'):
                pm.mel.eval('polyCrunch')
            for po in pm.ls(typ='polygonCruncherSettingsNode'):
                # pm.mel.eval('pcPressCalculateButton("{}.calculate")'.format(po.name()))
                pm.mel.eval('setAttr "{}.autoCalculate" 1'.format(po.name()))
                # pm.mel.eval('setAttr "polygonCruncherSettingsNode1.optimizationRatio" 10')
                pm.mel.eval('setAttr "{}.optimizationRatio" 20'.format(po.name()))
            pm.delete(ch=True)

            # 判断是否有切割好的身体，如果有说明是二级角色，需要与睁眼的头合并
            if nohead_body:
                # 复制一份睁眼头颅与切割好的身体合并
                polygon_head_eye_open = cmds.duplicate(self.dialog.temp_head, name='polygon_head_eye_open', rr=True)[0]
                combined = cmds.polyUnite(
                    [polygon_head_eye_open, nohead_body],
                    ch=False,  # 不保留 construction history
                    mergeUVSets=True
                )[0]
                pm.delete(ch=True)
                new_name = cmds.rename(combined, 'body_geo')
                cmds.parent(new_name, '|master|poly|to_lay|mesh_grp|skin_grp')

            if not os.path.exists(os.path.join(os.path.dirname(pm.sceneName()), 'to_lay')):
                os.mkdir(os.path.join(os.path.dirname(pm.sceneName()), 'to_lay'))
            if os.path.exists(os.path.join(os.path.dirname(pm.sceneName()), 'to_lay', os.path.basename(pm.sceneName()))):
                os.remove(os.path.join(os.path.dirname(pm.sceneName()), 'to_lay', os.path.basename(pm.sceneName())))

            # 选择导出
            cmds.select(cl=1)
            pm.select(pm.listRelatives(to_lay, ad=True, typ='mesh'))
            if hair:
                pm.select(pm.listRelatives(hair, ad=True, typ='mesh'), add=True)
            if face_pass_hair:
                pm.select(pm.listRelatives(face_pass_hair, ad=True, typ='mesh'), add=True)
            # pm.exportSelected(os.path.join(os.path.dirname(pm.sceneName()), 'to_lay', os.path.basename(pm.sceneName())))
            pm.mel.eval('file -force -options "v=0;" -typ "mayaAscii" -pr -es "{}";'.format(os.path.join(os.path.dirname(pm.sceneName()), 'to_lay', os.path.basename(pm.sceneName())).replace('\\', '/')))

            # 清理复制的物体
            pm.delete(to_lay)
            if hair:
                pm.delete(hair)
            if face_pass_hair:
                pm.delete(face_pass_hair)
            for h in pm.ls('*polygon_hair*'):
                pm.delete(h)
            return ''
        except:
            for h in pm.ls('*polygon_hair*'):
                pm.delete(h)
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
