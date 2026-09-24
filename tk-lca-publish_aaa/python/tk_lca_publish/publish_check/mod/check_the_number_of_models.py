# -*- coding:utf-8 -*-
############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author:
#
# Date: 2025.04
#
# Description: Check the number of model faces
#
############################################
import os
import re
import maya.api.OpenMaya as om
import pymel.core as pm
import maya.cmds as cmds
import traceback
from proc.function_running_time import record_time

class Octree_model():
    def __init__(self,center,size,depth=0,max_depth=4):
        """初始化当前八叉树节点

        Args:
            center (_type_): cube的中心点
            size (_type_): cube的半边长
            depth (int, optional): 当前的深度
            max_depth (int, optional): 最大深度
        """        
        self.center = center
        # 一半的边长
        self.size = size
        self.depth = depth
        self.max_depth = max_depth
        # 有就是分过，一旦分过里面就装了八个节点构成的八叉树节点
        self.children = []
        # 存储 (shape_path, face_index)
        self.faces = []
        self.face_count = 0
        self.min_length= 0
    def contains(self,pos):
        """判断一个点是否落在当前 cube 的范围内 三维数据判断

        Args:
            pos (_type_): 三维坐标 (x, y, z)
        """        
        x, y, z = pos
        cx, cy, cz = self.center
        hs = self.size
        return (cx - hs <= x <= cx + hs and
                cy - hs <= y <= cy + hs and
                cz - hs <= z <= cz + hs)
    def subdivide(self):
        """把当前 cube 划分成 8 个子 cube。每个子 cube 创建一个新的 OctreeNode 实例，加入到当前节点的self.children内
        """ 
        # 拆分出来的子cube的半边长
        hs = self.size / 2.0
        offsets = [-hs, hs]
        # 遍历所有 8 个三轴方向的组合生成子节点的中心点
        for dx in offsets:
            for dy in offsets:
                for dz in offsets:
                    child_center = (self.center[0] + dx,
                                    self.center[1] + dy,
                                    self.center[2] + dz)
                    # 一旦切过了当前cube就是新的八个节点的父节点，它的children内加入这八个节点生成的八叉树
                    self.children.append(Octree_model(child_center, hs, self.depth + 1, self.max_depth))

    def insert(self,point,face_id):
        """把一个面中心点插入到正确的 cube 中

        Args:
            point (_type_): 某个要判断的面的中心点
        """        
        # 如果已经达到最大深度，就直接在当前节点记录这个面 这就是终止条件
        if self.depth >= self.max_depth:  

            self.faces.append(face_id)
            self.face_count += 1
            return 
        # 划分过没有：
        if not self.children:
            self.subdivide()
        # 对八个节点进行操作    
        for child in self.children:
            if child.contains(point):
                child.insert(point,face_id)
                return
        # 点刚好落在 cube 边界，但浮点数误差导致所有子节点都判断为 false 就也记下来
        self.faces.append(face_id)        
        self.face_count += 1
    def gather_density_regions(self,regions, threshold):
        if self.children:
            for child in self.children:
                child.gather_density_regions(regions,threshold)
        else:
            if self.face_count>=threshold:
                regions.append({
                "center": self.center,
                "face_count": self.face_count,
                "face_ids": self.faces 
            })

def calculate_box_global(face_centers):
    """计算模型的包围盒的中心和半边长

    Args:
        face_centers (list): 所有面中心的列表

    Returns:
        int: 大包围盒的中心和半边长
    """  
    positions = [center for (_, _, center) in face_centers]
    xs, ys, zs = zip(*positions)
    max_x,min_x = max(xs),min(xs)
    max_y,min_y = max(ys),min(ys)
    max_z,min_z = max(zs),min(zs)
    center =  ((min_x + max_x)/2.0, (min_y + max_y)/2.0, (min_z + max_z)/2.0)
    size = max(max_x-min_x, max_y-min_y, max_z-min_z) / 2.0
    return center,size
def analyze(all_centers,max_depth,density_threshold):
    # 算出整个模型box的中心和size
    center,size = calculate_box_global(all_centers)
    root = Octree_model(center, size, max_depth=max_depth)
    leaf_size = size / (2 ** max_depth)
    # 插入所有面中心点
    # 每个面中心点依次被丢进八叉树
    for shape, face_index, f_center in all_centers:
        root.insert(f_center,(shape, face_index))

    # 最后算密度
    high_density_regions=[]
    root.gather_density_regions(high_density_regions, threshold=density_threshold)
    return high_density_regions



def get_selected_dag_path():
    """获得模型所有mesh对象的DAG路径

    Returns:
        MDagPath: _description_
    """    
    sel = om.MSelectionList()
    # 选中hi开始操作
    sel.add("|master|poly|hi") 
    dag_path = sel.getDagPath(0)
    # 创建一个 DAG 遍历器（深度优先）
    it_dag = om.MItDag(om.MItDag.kDepthFirst)
    # 从 master 开始递归遍历所有子节点
    it_dag.reset(dag_path, om.MItDag.kDepthFirst)
    mesh_paths = []
    while not it_dag.isDone():
        path = it_dag.getPath()
        if path.apiType() == om.MFn.kMesh:
            fn_mesh = om.MFnMesh(path)
            if not fn_mesh.isIntermediateObject:
                mesh_paths.append(path)
        it_dag.next()
    return mesh_paths


def get_face_centers(mesh_paths):
    """获得所有shape的mesh的所有中心点
    Args:
        mesh_paths (MDagPath): 所有shape的DAG路径

    Returns:
        list: 所有(shape_path_str, face_local_index, center_point)
    """    
    # 存储所有的中心点
    centers=[]
    face_id = 0
    # 对每一个shape
    for path in mesh_paths:
        mesh_fn = om.MFnMesh(path)
        # 这个得出来的序号是针对每个shape的 但是放到全局就不是这样了所以需要让列表记住shape
        all_points = mesh_fn.getPoints(om.MSpace.kWorld)
        # 拿到这个shape的全路径名字
        shape_name = path.fullPathName()
        # 对这个shape的每一个mesh计算出中心点 
        for i in range(mesh_fn.numPolygons):
            vert_ids = mesh_fn.getPolygonVertices(i)
            center = om.MVector(0.0, 0.0, 0.0)
            for vid in vert_ids:
                p = all_points[vid]
                center += om.MVector(p.x, p.y, p.z)
            center /= len(vert_ids)
            # centers存储每个mesh的中心点
            centers.append((shape_name,i,(center.x, center.y, center.z)))
    return centers

def clear_old_locators():
    if cmds.objExists("density_locators"):
        try:
            cmds.delete("density_locators")
        except Exception as e:
            print("删除旧的 density_locators 失败：{}".format(e))
def get_color_gradient(normalized_density):
    if normalized_density < 0.25:
        return (0, normalized_density * 4, 1)
    elif normalized_density < 0.5:
        return (0, 1, 1 - (normalized_density - 0.25) * 4)
    elif normalized_density < 0.75:
        return ((normalized_density - 0.5) * 4, 1, 0)
    else:
        return (1, 1 - (normalized_density - 0.75) * 4, 0)
        
class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查模型总面数和模型面数是否均匀"
        self.description = u"检查模型总面数和模型面数是否均匀。如果模型超过了当前角色级别的限制面数，就自动会显示一个Locator组，按照色相排列从蓝到红地标注了面数更密的区域，辅助艺术家进行减面。 skip tag : face_cnt, 单体超过万面： leader_check_proportion"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def check_density(self):
        mesh_paths = get_selected_dag_path()
        clear_old_locators()
        centers_list = get_face_centers(mesh_paths)
        regions = analyze(centers_list, max_depth=4, density_threshold=24)
        max_density = max([r['face_count'] for r in regions])
        cmds.select(clear=True)
        group_name = cmds.group(em=True, name="density_locators")
        for i, region in enumerate(regions):
            norm_density = float(region['face_count']) / max_density
            r, g, b = get_color_gradient(norm_density)
            try:
                loc = cmds.spaceLocator()[0]
                cmds.xform(loc, ws=True, t=region['center'])
                cmds.setAttr(loc + ".overrideEnabled", 1)
                cmds.setAttr(loc + ".overrideRGBColors", 1)
                cmds.setAttr(loc + ".overrideColorRGB", r, g, b)
                cmds.setAttr(loc + ".localScaleX", 0.15)
                cmds.setAttr(loc + ".localScaleY", 0.15)
                cmds.setAttr(loc + ".localScaleZ", 0.15)
                cmds.parent(loc, group_name)
            except Exception as e:
                print("Locator 创建失败：{} - 错误：{}".format(region['center'], e))
        cmds.select(clear=True)

    # 检查模型是否大于shotgun项目上的上限值
    def check_mod_face_count(self, tags):
        file_path = pm.sceneName()
        if ".model_lite." in file_path:
            if "leader_check_lite_face" in tags:
                return [False, u""]
            poly_mesh = cmds.listRelatives('|master|poly', ad=True, type='mesh',fullPath=True)
            if not poly_mesh:
                return [True, u"没找到模型"]
        if "face_cnt" in tags:
            return [False, u""]

        sg_diffculty = {"1": 'sg_difficulty_one_level', "2": "sg_difficulty_secondary_level", "3": 'sg_difficulty_three_level'}
        sg_level_count = self.dialog.sg.find_one('Project', [['name', "is", self.dialog.project['name'].upper()]],['sg_difficulty_one_level', 'sg_difficulty_secondary_level', 'sg_difficulty_three_level'])
        sg_asset_level = self.dialog.sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name'].upper()], ['id', 'is', self.dialog.entity['id']]], ['sg_diffculty2'])
        if not sg_asset_level['sg_diffculty2'] or sg_asset_level['sg_diffculty2'] == "4":
            asset_level = 'sg_difficulty_three_level'
        else:
            asset_level = sg_diffculty[sg_asset_level['sg_diffculty2']]
        #得到不同級別角色的面數標準 一級無要求 二級350000 三級100000
        level_count = sg_level_count[asset_level]

        if level_count == None:
            return [False, u""]

        list_mesh = cmds.listRelatives('|master|poly|hi|', ad=True, type='mesh',fullPath=True)
        if not list_mesh:
            return [True, u"没找到模型"]

        cmds.select(list_mesh)
        face_num = cmds.polyEvaluate(f=True)
        if int(level_count) >= int(face_num):
            clear_old_locators()
            return [False,""]
        else:
            self.check_density()
            if sg_asset_level['sg_diffculty2']:
                messge_ = u"当前资产为{0}级模型，shotgun上对{0}级模型的最高面数的上限是{1},当前模型的面数为{2}，请让leader检查!\n如果需要跳过请联系总监或组长在shotgun tags上标注 '' face_cnt ''\n面数过密的局部区域已用Locator显示! 如果下次提交拍屏则需要删去density_locators组".format(str(sg_asset_level['sg_diffculty2']), str(level_count), str(face_num))
            else:
                messge_ = u"当前资产为{0}级模型，shotgun上对{0}级模型的最高面数的上限是{1},当前模型的面数为{2}，请让leader检查!\n如果需要跳过请联系总监或组长在shotgun tags上标注 '' face_cnt ''\n面数过密的局部区域已用Locator显示! 如果下次提交拍屏则需要删去density_locators组。".format(u"3", str(level_count), str(face_num))
            return [True, messge_]

    # 按资产比较检查单个物体（shape）面数是否过高
    def check_by_asset_ratio(self, tags):
        if "leader_check_proportion" in tags:
            return [False, u""]

        list_mesh = cmds.listRelatives('|master|poly|hi|', ad=True, type='mesh',fullPath=True)
        poly_hi_grp = cmds.ls("|master|poly|hi")[0]
        if not list_mesh and poly_hi_grp:
            return [True, u"没找到模型"]

        hi_volume = self.get_boundingBox_volume("|master|poly|hi|")
        cmds.select(list_mesh)
        face_num = cmds.polyEvaluate(f=True)

        cmds.select(list_mesh)
        all_mesh = cmds.ls(type="mesh", l=True)
        excessive_size_error = []
        proportion_density_error = []
        for obj in all_mesh:
            obj_face_count = cmds.polyEvaluate(obj, face=True)
            if u'|master|poly|hi|' in obj:
                if u"|body_geoShape" in obj:
                    continue
                transform_node = cmds.listRelatives(obj, parent=True, fullPath=True)[0]
                obj_volume = self.get_boundingBox_volume(transform_node)
                # volume小于等于 1 的mesh 不能超过两万面
                if obj_volume <= 1.0 and obj_face_count > 20000:
                    excessive_size_error.append(obj)

                if obj_volume == 0:
                    continue
                bbox_proportion = hi_volume/obj_volume
                # 角色当个物体是总面数的一半就需要leader检查（暂定为0.5）
                face_count_proportion = face_num * 0.5
                # 大小比例暂定为0.00005，后面有问题再测试
                if bbox_proportion < 0.00005 and obj_face_count > face_count_proportion:
                    proportion_density_error.append(obj)

        if excessive_size_error:
            messge_ = u"\n".join(excessive_size_error) + u"： \n以上这些物体面数超过了2万面，请让leader检查！\n如果需要跳过请联系总监或组长在shotgun tags上标注 '' leader_check_proportion ''"
            return [True, messge_]

        if proportion_density_error:
            messge_ = u"\n".join(proportion_density_error) + u"： \n以上这些物体比例较小而且面数超过了总面数的一半，请让leader检查！\n如果需要跳过请联系总监或组长在shotgun tags上标注 '' leader_check_proportion ''"
            return [True, messge_]

        return [False, u""]

    @record_time(__file__)
    def run_check(self):
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                if self.dialog.d_assets_info[asset_name]['type'] != 'chr':
                    return u""

            asset_tags = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['tags'])
            tags = [t['name'] for t in asset_tags['tags']]
            # 取消poly组下隐藏
            self.ensure_visibility('|master|poly')

            # 总面数检查
            check_face_count = self.check_mod_face_count(tags)
            # True False 有错误 就返回错误它就不为空了
            err_msg = []
            if check_face_count[0]:
                err_msg.append(check_face_count[1])

            # 单个模型面数和比例检查
            single_model_asset_ratio = self.check_by_asset_ratio(tags)
            if single_model_asset_ratio[0]:
                err_msg.append(single_model_asset_ratio[1])

            if err_msg:
                return u"\n".join(err_msg)
            else:
                return u""

        except:
            return traceback.format_exc()
    def ensure_visibility(self,root):
        if cmds.objExists(root):
            try:
                all_nodes = cmds.listRelatives(root, allDescendents=True, fullPath=True) or []
                all_nodes.append(root)
                for node in all_nodes:
                    if cmds.attributeQuery("visibility", node=node, exists=True):
                        try:
                            cmds.setAttr("{}.visibility".format(node), 1)
                        except Exception as e:
                            print("无法取消{}的隐藏状态".format(node))
            except Exception as e:
                print("不是对象状态改变失败的错误：{}".format(e))


    def get_boundingBox_volume(self, group_):
        bbox = cmds.xform(group_, query=True, boundingBox=True, worldSpace=True)
        width = bbox[3] - bbox[0]
        height = bbox[4] - bbox[1]
        depth = bbox[5] - bbox[2]
        volume = width * height * depth
        return volume

    def run_fix(self):
        '''Auto Fix'''

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
