# -*- coding: utf-8 -*-

import string
import json,os,sys,shutil,traceback,re,platform,string
import ani.lca_asset_switch.switch_rig_new as srn
from production import shotgun_connection
sg = shotgun_connection.Connection('get_shot_info').get_sg()
import production.mayautils as mutils
skip_switch_tech_rig_flag = 'cache_skip_switch_tech_rig'

systemVersion = platform.platform()
if 'Window' in systemVersion:
    LOOKDIFF_3_HAIR_INFO_DIR = 'W:/shome/PLETEMP/TD_SHOT/lookdiff_3_hair_info/%s/asset/%s/'
else:
    LOOKDIFF_3_HAIR_INFO_DIR = '/mnt/work/shome/PLETEMP/TD_SHOT/lookdiff_3_hair_info/%s/asset/%s/'

def get_rig_task_tag_from_shotgun(proj, asset_name, rig_type):
    step = 'Rig'

    rig_task_filters = [
        ["project.Project.name", "is", proj],
        ["entity", "name_is", asset_name],  # name_contains -- is
        ["step", "name_is", step],
        ["content", "is", rig_type],
        ["sg_status_list", "is_not", 'omt'],
        # ['sg_last_version.Version.sg_version_type', 'is', 'Downstream']
    ]

    rig_task_info = sg.find_one('Task', rig_task_filters, ['tags'])
    # print(rig_task_info)

    tagNameList = []
    if rig_task_info:
        rig_task_tags = rig_task_info['tags']
        for tag in rig_task_tags:
            tagNameList.append(tag['name'])

    return tagNameList

def get_shot_tag_from_shotgun(proj, shot):
    shot_tags = sg.find_one('Shot',
                            [['project', 'name_is', proj],
                             ['code', 'is', shot]],
                            ["tags"])

    tagNameList = []
    if shot_tags:
        shot_tags = shot_tags["tags"]
        for tag in shot_tags:
            tagNameList.append(tag["name"])

    return tagNameList

def get_selected_references():
    """获取已勾选的引用文件"""
    selected_refs = []
    
    all_refs = cmds.file(query=True, reference=True) or []
    
    for ref_path in all_refs:
        try:
            is_deferred = cmds.file(ref_path, query=True, deferReference=True)
            if not is_deferred:
                selected_refs.append(ref_path)
        except:
            continue
    
    return selected_refs

def extract_namespace_from_node(node_path):
    """从节点路径提取名称空间"""
    if not node_path:
        return ""
    
    short_name = node_path.split('|')[-1]
    
    if ':' in short_name:
        return short_name.split(':')[0]
    
    return ""

def get_reference_namespaces(ref_path):
    """获取引用中非相机节点的名称空间"""
    namespaces = set()
    
    try:
        ref_nodes = cmds.referenceQuery(ref_path, nodes=True, dagPath=True) or []
        
        for node in ref_nodes:
            node_type = cmds.nodeType(node)
            if node_type == 'camera':
                continue
            
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
            is_camera = False
            for shape in shapes:
                if cmds.nodeType(shape) == 'camera':
                    is_camera = True
                    break
            
            if not is_camera:
                namespace = extract_namespace_from_node(node)
                if namespace:
                    namespaces.add(namespace)
    
    except Exception as e:
        print("获取引用名称空间时出错: {}".format(str(e)))
    
    return list(namespaces)


def get_transform_nodes_in_group(group_name, check_group=False):
    """获取组下所有transform节点的显示隐藏信息"""
    result = []
    
    if not cmds.objExists(group_name):
        return result
    
    # [NOTE]:获取组下的所有直接子transform节点
    child_transforms = cmds.listRelatives(group_name, 
                                            children=True,
                                            type='transform',
                                            fullPath=True) or []
    if check_group:
        child_transforms = [group_name]
    
    for child in child_transforms:
        # [NOTE]:获取显示状态
        visibility = True
        child_shapes = cmds.listRelatives(child, shapes=True, noIntermediate=True) or []
        child_check_vis = child if not child_shapes else child_shapes[0]
        try:
            if cmds.attributeQuery('visibility', node=child_check_vis, exists=True):
                vis_attr = "{}.visibility".format(child_check_vis)
                visibility = bool(cmds.getAttr(vis_attr))
        except:
            visibility = True
        
        node_info = {
            "transform_node": child,
            "visibility": visibility
        }
        
        result.append(node_info)
    
    return result


def get_transform_all_nodes_in_group(group_name, name_filter=None, muggle=False):
    """获取组下所有transform节点的显示隐藏信息"""
    result = []

    if not cmds.objExists(group_name):
        return result

    # [NOTE]:获取组下的所有直接子transform节点
    child_transforms = cmds.listRelatives(group_name,
                                            ad=True,
                                            type='transform',
                                            fullPath=True) or []

    for transform in child_transforms:
        # [NOTE]:获取显示状态
        short_name = transform.rsplit('|', 1)[-1]
        transform_shapes = cmds.listRelatives(transform, shapes=True, noIntermediate=True) or []
        transform_check_vis = transform if not transform_shapes else transform_shapes[0]
        try:
            if name_filter and not short_name.startswith(name_filter):
                continue
            if muggle:
                group_name = transform_check_vis
            visibility = is_visible_under_root(transform_check_vis, group_name)
        except:
            visibility = True

        node_info = {
            "transform_node": transform,
            "visibility": visibility
        }

        result.append(node_info)

    return result


def get_node_type_in_outliner(node):
    if cmds.nodeType(node) != 'transform':
        return cmds.nodeType(node)

    shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True) or []

    if not shapes:
        return 'group'

    shape_type = cmds.nodeType(shapes[0])

    if shape_type == 'mesh':
        return 'mesh'

    return shape_type


def is_visible_under_root(node, root_grp):
    current = node

    while current:
        if not cmds.getAttr(current + '.visibility'):
            return False

        if current == root_grp:
            break

        parent = cmds.listRelatives(current, p=True, f=True)
        current = parent[0] if parent else None

    return True


def get_RiggingSystemType(namespace):
    RiggingType = "lca"
    global_ctrl = "{}:global_ctrl".format(namespace)
    if cmds.objExists(global_ctrl):
        if cmds.objExists(global_ctrl + ".rig_system"):
            RiggingType = cmds.getAttr(global_ctrl + ".rig_system")
            # RiggingType == "adv"/"muggle"
    return RiggingType



def _readJson(jsonPath):
    with open(jsonPath) as json_file:
        json_data = json.load(json_file)
    return json_data

# def get_group_info_by_namespace_no_rule(namespace,lookdiff_3_hair_info_data):
#     """获取指定名称空间的组信息（包含所有transform节点） 
#     此处针对 不规范资产，需要提前单独将三个key对应的层级写入到json内
#     然后读取json，拿固定mesh层级，进行记录输出"""
#     result = {}
#     rig_type = get_RiggingSystemType(namespace)
#     muggle = True if rig_type == "muggle" else False
    
#     # [NOTE]:处理face_hair组 - 获取所有transform节点
#     face_hair_key = 'face_hair'
#     if face_hair_key in lookdiff_3_hair_info_data.keys():
#         if lookdiff_3_hair_info_data[face_hair_key]!=[]:
#             result["face_hair"] = []
#             for face_hair_group in lookdiff_3_hair_info_data[face_hair_key]:
#                 if cmds.objExists(face_hair_group):
#                     face_hair_group = cmds.ls(face_hair_group, long=True)[0]
#                     face_hair_transforms = get_transform_all_nodes_in_group(face_hair_group, muggle=muggle)
#                     face_hair_transforms = [i for i in face_hair_transforms
#                                             if get_node_type_in_outliner(i['transform_node']) == 'mesh']
#                     if face_hair_transforms:
#                         result["face_hair"] = result["face_hair"] + face_hair_transforms

#     # [NOTE]:处理head_hair组 - 获取所有transform节点
#     head_hair_key = 'head_hair'
#     if head_hair_key in lookdiff_3_hair_info_data.keys():
#         if lookdiff_3_hair_info_data[head_hair_key]!=[]:
#             result["head_hair"] = []
#             for head_hair_group in lookdiff_3_hair_info_data[head_hair_key]:
#                 if cmds.objExists(head_hair_group):
#                     head_hair_group = cmds.ls(head_hair_group, long=True)[0]
#                     head_hair_transforms = get_transform_all_nodes_in_group(head_hair_group, muggle=muggle)
#                     head_hair_transforms = [i for i in head_hair_transforms
#                                             if get_node_type_in_outliner(i['transform_node']) == 'mesh']
#                     if head_hair_transforms:
#                         result["head_hair"] = result["head_hair"] + head_hair_transforms

#     # [NOTE]:处理face_pass_grp组 - 获取所有transform节点
#     face_pass_key = 'face_pass'
#     if face_pass_key in lookdiff_3_hair_info_data.keys():
#         if lookdiff_3_hair_info_data[face_pass_key]!=[]:
#             result["face_pass"] = []
#             for face_pass_group in lookdiff_3_hair_info_data[face_pass_key]:
#                 if cmds.objExists(face_pass_group):
#                     face_pass_transforms = get_transform_nodes_in_group(face_pass_group)
#                     if face_pass_transforms:
#                         face_pass_result = []
#                         for fp in face_pass_transforms:
#                             if not fp['visibility']:
#                                 continue
#                             fp_result = get_transform_all_nodes_in_group(fp['transform_node'],
#                                                                                     '{}:shell_'.format(namespace),
#                                                                                     muggle=muggle)
#                             grp_vis_status = [i for i in fp_result if i['visibility']]
#                             if grp_vis_status:
#                                 face_pass_result.extend(fp_result)
#                         if face_pass_result:
#                             result["face_pass"] = result["face_pass"] + face_pass_result

#     # [NOTE]:处理cloth_pass_grp组 - 获取所有transform节点
#     cloth_pass_group = cmds.ls("{}:CLT_*_grp".format(namespace) if namespace else "cloth_pass_group", long=True)
#     if cloth_pass_group:
#         cloth_pass_result = []
#         for child in cloth_pass_group:
#             node_info = get_transform_all_nodes_in_group(child, muggle=muggle)
#             child_grp_vis = [i for i in node_info if i['visibility'] and
#                                 get_node_type_in_outliner(i['transform_node']) == 'mesh']
#             cloth_pass_result.append({"transform_node": child, "visibility": bool(child_grp_vis)})

#         if cloth_pass_result:
#             result["cloth_pass"] = cloth_pass_result
    
#     # [NOTE]:只有当有face_hair或head_hair信息时才返回
#     if result:
#         return result
    
#     return None



def _get_group_info_by_namespace(namespace,proj):
    """获取指定名称空间的组信息（包含所有transform节点）"""
    result = {}
    rig_type = get_RiggingSystemType(namespace)
    muggle = True if rig_type == "muggle" else False
    
    # [NOTE]:处理face_hair组 - 获取所有transform节点
    face_hair_group = "{}:face_hair".format(namespace) if namespace else "face_hair"
    if cmds.objExists(face_hair_group):
        face_hair_group = cmds.ls(face_hair_group, long=True)[0]
        face_hair_transforms = get_transform_all_nodes_in_group(face_hair_group, muggle=muggle)
        face_hair_transforms = [i for i in face_hair_transforms
                                if get_node_type_in_outliner(i['transform_node']) == 'mesh']
        if face_hair_transforms:
            result["face_hair"] = face_hair_transforms
    
    # [NOTE]:处理head_hair组 - 获取所有transform节点
    #　获取真实名字，而非名称空间，为了更准确获取中间存放的json路径
    _asset_name  = namespace.rstrip(string.digits)
    # 获取中间存放的json文件夹
    lookdiff_3_hair_info_dir = LOOKDIFF_3_HAIR_INFO_DIR % (proj,_asset_name)
    # 获取中间存放的json文件
    lookdiff_3_hair_info_json_path = lookdiff_3_hair_info_dir+'/lookdiff_3_hair_info.json'
    print 'lookdiff_3_hair_info_dir >>>>>',lookdiff_3_hair_info_dir
    print 'lookdiff_3_hair_info_json_path >>>>>',lookdiff_3_hair_info_json_path

    # 当二者都存在时，才去做 不按照流程制作资产 的方式去获取 head_hair
    if os.path.exists(lookdiff_3_hair_info_dir) and os.path.exists(lookdiff_3_hair_info_json_path):
        print '>>> do no rule chr head_hair lookdiff_3_hair_info_json >>>'
        lookdiff_3_hair_info_data = _readJson(lookdiff_3_hair_info_json_path)
        head_hair_key = 'head_hair'
        # 查询有无 head_hair key 在json字典内，没有也不做处理
        if head_hair_key in lookdiff_3_hair_info_data.keys():
            if lookdiff_3_hair_info_data[head_hair_key]!=[]:
                result["head_hair"] = []
                for _head_hair_group in lookdiff_3_hair_info_data[head_hair_key]:
                    # 获取字典内记录的层级，一般是组，需要往下查找mesh的隐藏显示情况
                    # 只有像 labourer_e 特殊情况，需要记录mesh，然后往上层找组的显示隐藏
                    head_hair_group = _head_hair_group.replace(_asset_name,namespace)
                    if cmds.objExists(head_hair_group):
                        head_hair_group = cmds.ls(head_hair_group, long=True)[0]
                        # 如果是 labourer_e 特殊资产，通过 json 记录的 mesh，往上层找组的显示隐藏
                        # 如果是 labourer_d 特殊资产，通过 json 记录的 mesh，直接获取其显示隐藏
                        # 其他情况，则是通过 json 记录的 组，往下层找mesh的显示隐藏
                        if _asset_name == 'labourer_e':
                            # head_hair_group_parent = os.path.dirname(head_hair_group.replace('|','/')).replace('/','|')
                            head_hair_group_parent = cmds.listRelatives(head_hair_group,p=1,fullPath=1)[0]
                            head_hair_group_parent_vis = cmds.getAttr(head_hair_group_parent + '.visibility')
                            head_hair_transforms = {}
                            head_hair_transforms['transform_node'] = head_hair_group
                            head_hair_transforms['visibility'] = head_hair_group_parent_vis
                            result["head_hair"].append(head_hair_transforms)
                        elif _asset_name == 'labourer_d':
                            head_hair_group_vis = cmds.getAttr(head_hair_group + '.visibility')
                            head_hair_transforms = {}
                            head_hair_transforms['transform_node'] = head_hair_group
                            head_hair_transforms['visibility'] = head_hair_group_vis
                            result["head_hair"].append(head_hair_transforms)
                        else:
                            head_hair_transforms = get_transform_all_nodes_in_group(head_hair_group, muggle=muggle)
                            head_hair_transforms = [i for i in head_hair_transforms
                                                    if get_node_type_in_outliner(i['transform_node']) == 'mesh']
                            if head_hair_transforms:
                                result["head_hair"] = result["head_hair"] + head_hair_transforms
        else:
            print '>>> do rule chr head_hair lookdiff_3_hair_info_json >>>'
            head_hair_group = "{}:head_hair".format(namespace) if namespace else "head_hair"
            if cmds.objExists(head_hair_group):
                head_hair_group = cmds.ls(head_hair_group, long=True)[0]
                head_hair_transforms = get_transform_all_nodes_in_group(head_hair_group, muggle=muggle)
                head_hair_transforms = [i for i in head_hair_transforms
                                        if get_node_type_in_outliner(i['transform_node']) == 'mesh']
                if head_hair_transforms:
                    result["head_hair"] = head_hair_transforms
    else:
        print '>>> do rule chr head_hair lookdiff_3_hair_info_json >>>'
        head_hair_group = "{}:head_hair".format(namespace) if namespace else "head_hair"
        if cmds.objExists(head_hair_group):
            head_hair_group = cmds.ls(head_hair_group, long=True)[0]
            head_hair_transforms = get_transform_all_nodes_in_group(head_hair_group, muggle=muggle)
            head_hair_transforms = [i for i in head_hair_transforms
                                    if get_node_type_in_outliner(i['transform_node']) == 'mesh']
            if head_hair_transforms:
                result["head_hair"] = head_hair_transforms

    # 当二者都存在时，才去做 不按照流程制作资产 的方式去获取 face_pass
    if os.path.exists(lookdiff_3_hair_info_dir) and os.path.exists(lookdiff_3_hair_info_json_path):
        print '>>> do no rule chr face_pass lookdiff_3_hair_info_json >>>'
        lookdiff_3_hair_info_data = _readJson(lookdiff_3_hair_info_json_path)
        face_pass_key = 'face_pass'
        # 查询有无 face_pass key 在json字典内，没有也不做处理
        if face_pass_key in lookdiff_3_hair_info_data.keys():
            if lookdiff_3_hair_info_data[face_pass_key]!=[]:
                result["face_pass"] = []
                for _face_pass_group in lookdiff_3_hair_info_data[face_pass_key]:
                    face_pass_group = _face_pass_group.replace(_asset_name,namespace)
                    # 只有像 labourer_d 特殊情况，通过 json 记录的 mesh，直接获取其显示隐藏
                    if cmds.objExists(face_pass_group):
                        face_pass_group = cmds.ls(face_pass_group, long=True)[0]
                        if _asset_name == 'labourer_d':
                            face_pass_group_vis = cmds.getAttr(face_pass_group + '.visibility')
                            face_pass_transforms = {}
                            face_pass_transforms['transform_node'] = face_pass_group
                            face_pass_transforms['visibility'] = face_pass_group_vis
                            result["face_pass"].append(face_pass_transforms)
        else:
            print '>>> do rule chr face_pass lookdiff_3_hair_info_json >>>'
            # [NOTE]:处理face_pass_grp组 - 获取所有transform节点
            face_pass_group = "{}:face_pass_grp".format(namespace) if namespace else "face_pass_grp"
            if cmds.objExists(face_pass_group):
                face_pass_transforms = get_transform_nodes_in_group(face_pass_group)
                if face_pass_transforms:
                    face_pass_result = []
                    for fp in face_pass_transforms:
                        if not fp['visibility']:
                            continue
                        fp_result = get_transform_all_nodes_in_group(fp['transform_node'],
                                                                                '{}:shell_'.format(namespace),
                                                                                muggle=muggle)
                        grp_vis_status = [i for i in fp_result if i['visibility']]
                        if grp_vis_status:
                            face_pass_result.extend(fp_result)
                    if face_pass_result:
                        result["face_pass"] = face_pass_result
    else:
        print '>>> do rule chr face_pass lookdiff_3_hair_info_json >>>'
        # [NOTE]:处理face_pass_grp组 - 获取所有transform节点
        face_pass_group = "{}:face_pass_grp".format(namespace) if namespace else "face_pass_grp"
        if cmds.objExists(face_pass_group):
            face_pass_transforms = get_transform_nodes_in_group(face_pass_group)
            if face_pass_transforms:
                face_pass_result = []
                for fp in face_pass_transforms:
                    if not fp['visibility']:
                        continue
                    fp_result = get_transform_all_nodes_in_group(fp['transform_node'],
                                                                            '{}:shell_'.format(namespace),
                                                                            muggle=muggle)
                    grp_vis_status = [i for i in fp_result if i['visibility']]
                    if grp_vis_status:
                        face_pass_result.extend(fp_result)
                if face_pass_result:
                    result["face_pass"] = face_pass_result

    # [NOTE]:处理cloth_pass_grp组 - 获取所有transform节点
    cloth_pass_group = cmds.ls("{}:CLT_*_grp".format(namespace) if namespace else "cloth_pass_group", long=True)
    if cloth_pass_group:
        cloth_pass_result = []
        for child in cloth_pass_group:
            node_info = get_transform_all_nodes_in_group(child, muggle=muggle)
            child_grp_vis = [i for i in node_info if i['visibility'] and
                                get_node_type_in_outliner(i['transform_node']) == 'mesh']
            cloth_pass_result.append({"transform_node": child, "visibility": bool(child_grp_vis)})

        if cloth_pass_result:
            result["cloth_pass"] = cloth_pass_result
    
    # [NOTE]:只有当有face_hair或head_hair信息时才返回
    if result:
        return result
    
    return None

def get_group_info_by_namespace(namespace):
    """获取指定名称空间的组信息（包含所有transform节点）"""
    result = {}
    rig_type = get_RiggingSystemType(namespace)
    muggle = True if rig_type == "muggle" else False
    
    # [NOTE]:处理face_hair组 - 获取所有transform节点
    face_hair_group = "{}:face_hair".format(namespace) if namespace else "face_hair"
    if cmds.objExists(face_hair_group):
        face_hair_group = cmds.ls(face_hair_group, long=True)[0]
        face_hair_transforms = get_transform_all_nodes_in_group(face_hair_group, muggle=muggle)
        face_hair_transforms = [i for i in face_hair_transforms
                                if get_node_type_in_outliner(i['transform_node']) == 'mesh']
        if face_hair_transforms:
            result["face_hair"] = face_hair_transforms
    
    # [NOTE]:处理head_hair组 - 获取所有transform节点
    head_hair_group = "{}:head_hair".format(namespace) if namespace else "head_hair"
    if cmds.objExists(head_hair_group):
        head_hair_group = cmds.ls(head_hair_group, long=True)[0]
        head_hair_transforms = get_transform_all_nodes_in_group(head_hair_group, muggle=muggle)
        head_hair_transforms = [i for i in head_hair_transforms
                                if get_node_type_in_outliner(i['transform_node']) == 'mesh']
        if head_hair_transforms:
            result["head_hair"] = head_hair_transforms

    # [NOTE]:处理face_pass_grp组 - 获取所有transform节点
    face_pass_group = "{}:face_pass_grp".format(namespace) if namespace else "face_pass_grp"
    if cmds.objExists(face_pass_group):
        face_pass_transforms = get_transform_nodes_in_group(face_pass_group)
        if face_pass_transforms:
            face_pass_result = []
            for fp in face_pass_transforms:
                if not fp['visibility']:
                    continue
                fp_result = get_transform_all_nodes_in_group(fp['transform_node'],
                                                                        '{}:shell_'.format(namespace),
                                                                        muggle=muggle)
                grp_vis_status = [i for i in fp_result if i['visibility']]
                if grp_vis_status:
                    face_pass_result.extend(fp_result)
            if face_pass_result:
                result["face_pass"] = face_pass_result

    # [NOTE]:处理cloth_pass_grp组 - 获取所有transform节点
    cloth_pass_group = cmds.ls("{}:CLT_*_grp".format(namespace) if namespace else "cloth_pass_group", long=True)
    if cloth_pass_group:
        cloth_pass_result = []
        for child in cloth_pass_group:
            node_info = get_transform_all_nodes_in_group(child, muggle=muggle)
            child_grp_vis = [i for i in node_info if i['visibility'] and
                                get_node_type_in_outliner(i['transform_node']) == 'mesh']
            cloth_pass_result.append({"transform_node": child, "visibility": bool(child_grp_vis)})

        if cloth_pass_result:
            result["cloth_pass"] = cloth_pass_result
    
    # [NOTE]:只有当有face_hair或head_hair信息时才返回
    if result:
        return result
    
    return None

def process_all_namespaces(namespaces,scene_name):
    """处理所有名称空间，获取组信息"""
    #type: list[str]-> dict
    namespace_data = {}
    proj = scene_name.split('/projects/')[-1].split('/')[0]

    for namespace in namespaces:
        namespace_key = namespace if namespace else "global"

        # 原来脚本是 group_info = get_group_info_by_namespace(namespace)
        # 这里在增加处理 不按流程来走的资产
        # 会读取每个资产记录在 /mnt/work/shome/PLETEMP/TD_SHOT/lookdiff_3_hair_info/{proj}/asset/{namespace}/ 路径下的 json 文件
        # 目前只去处理 head_hair，其余获取逻辑不变
        # get_group_info_by_namespace_no_rule 是对 face_hair head_hair face_pass 三个都进行处理，获取中间json来进行记录输出
        # 跟 育顺 沟通过后，目前先只针对处理 head_hair
        # 脚本未删除，可做后续参考(注意，这个 get_group_info_by_namespace_no_rule 函数内并未对名称空间做处理，当先有后缀数字情况)

        # lookdiff_3_hair_info_dir = LOOKDIFF_3_HAIR_INFO_DIR % (proj,namespace)
        # lookdiff_3_hair_info_json_path = lookdiff_3_hair_info_dir+'/lookdiff_3_hair_info.json'
        
        # if os.path.exists(lookdiff_3_hair_info_dir) and os.path.exists(lookdiff_3_hair_info_json_path):
        #     lookdiff_3_hair_info_data = _readJson(lookdiff_3_hair_info_json_path)
        #     group_info = get_group_info_by_namespace_no_rule(namespace,lookdiff_3_hair_info_data)
        # else:
        #     group_info = get_group_info_by_namespace(namespace)

        group_info = _get_group_info_by_namespace(namespace,proj)
        
        if group_info:
            namespace_data[namespace_key] = group_info
    
    return namespace_data


def get_hair_pass_info(scene_name):
    #type:(...)->dict
    loaded_refs = get_selected_references()
    
    if not loaded_refs:
        print("未找到已勾选的引用")
        return {}

    all_namespaces = set()
    for ref_path in loaded_refs:
        try:
            ref_name = os.path.basename(ref_path)
            print("\n处理引用: {}".format(ref_name))

            namespaces = get_reference_namespaces(ref_path)
            if namespaces:
                print("  找到名称空间: {}".format(", ".join(namespaces)))
                all_namespaces.update(namespaces)
            else:
                print("  未找到有效的名称空间")
                
        except Exception as e:
            print("  处理引用时出错: {}".format(str(e)))
            continue
    
    all_data = process_all_namespaces(list(all_namespaces),scene_name)
    
    return all_data

def write_extra_data(extra_data_dir,extra_data,json_name):
        
    extra_data_json = os.path.join(extra_data_dir,json_name).replace('\\','/')
    print '>>>>>>>>>>>>>>>> extra_data_json',extra_data_json
    _writeJson(extra_data_json,extra_data)
def _writeJson(jsonPath, json_dict):
    try:
        extra_data_dir = os.path.dirname(jsonPath)
        os.system("chmod 777 -R %s" % extra_data_dir)
        os.chmod(extra_data_dir, 0777)
        #[NOTE]:publish经常有无权限的错误，这里给jsonpath 解锁
        os.system("chmod 777 -R %s" % jsonPath)
        os.chmod(jsonPath, 0777)
    except:
        pass

    with open(jsonPath, 'w') as json_file:
        json_file.write(json.dumps(json_dict, indent=4))
    
    try:
        extra_data_dir = os.path.dirname(jsonPath)
        os.system("chmod 777 -R %s" % extra_data_dir)
        os.chmod(extra_data_dir, 0777)
        #[NOTE]:publish经常有无权限的错误，这里给jsonpath 解锁
        os.system("chmod 777 -R %s" % jsonPath)
        os.chmod(jsonPath, 0777)
    except:
        pass


def switch_tech_rig(scene_name):

    _project = scene_name.split('/projects/')[-1].split('/')[0]
    _shots = scene_name.split('/ani/')[0].split('/')[-1]
    print '???????????????????',_project,_shots

    all_masters = cmds.ls('*:master',long=1)

    rfn_list = []
    for _transform in all_masters:
        
        if '|chr|' in _transform or '|crd|' in _transform or '|rra|' in _transform:
            transform = _transform.split('|')[-1]
            namespace = transform.split(':')[0]

            ref_top_rn = cmds.referenceQuery(transform, referenceNode=True, topReference=True)
            reference_file = cmds.referenceQuery(ref_top_rn, filename=True)
            file_rfn = srn.getReferencesFromNodes(transform)

            # if mod or switch specify rig, skip switch to rig
            skip_switch_tech = False

            # 1.1. skip -- skip mod switch to tech rig
            if '.mod.model' in reference_file:
                skip_switch_tech = True
                mutils.log('Mod skip switch tech rig ......')

            # 1.2. skip -- skip special rig switch to tech rig
            if '.rig.rigging' in reference_file:
                current_rig_type = reference_file.split('/publish/')[-1].split('/')[0].split('.')[-1]
                rig_task_tagNameList = get_rig_task_tag_from_shotgun(_project, re.sub(r'\d+$', '', namespace),
                                                                    current_rig_type)
                print('rig_task_tagNameList: ', rig_task_tagNameList)
                if skip_switch_tech_rig_flag in rig_task_tagNameList:
                    skip_switch_tech = True
                    mutils.log('Special rig skip switch tech rig ......')

            # 2.1 switch specify -- switch specify rig rigging_jointMatrix
            tagNameList = get_shot_tag_from_shotgun(_project, _shots)

            # 2.2 switch specify -- switch specify rig for shot specify tag
            try:
                for i in tagNameList:
                    if '.rig.rigging' in i and transform.split(':')[0] in i:
                        srn.main(i.split('.')[-1], show_ui=False, sel_rfn=file_rfn)
                        skip_switch_tech = True
                        mutils.log('Switch {} rig success ......'.format(i))
                        break
            except:
                mutils.log('Switch special rig failed ......')
                
            mutils.log('[INFO] Skip Switch Tech Result: {} ......'.format(skip_switch_tech))

            if skip_switch_tech:
                pass
            else:
                # file_rfn = srn.getReferencesFromNodes(transform)
                srn.main("tech", show_ui=False, sel_rfn=file_rfn)

                mutils.log('Switch tech rig success ......')
            

def main(maya_file, start_frame, end_frame):
    try:
        import maya.standalone
        # import pymel.core as pm
        import maya.mel as mel
        import maya.cmds as cmds
        maya.standalone.initialize(name='python')
        cmds.file(maya_file, open=True, force=True)

        scene_name = maya_file

        switch_tech_rig(scene_name)
        
        
        extra_data_hair_pass_info = get_hair_pass_info(scene_name) #type:dict
        
        # print shot_pass_attr_dict
        extra_data_dir_shot=os.path.dirname(scene_name)+'/extra_data'
        # print extra_data_dir_shot
        if not os.path.exists(extra_data_dir_shot):
            os.makedirs(extra_data_dir_shot)
        print '>>>>>>>>>>>>>>>> extra_data_dir_shot',extra_data_dir_shot
        write_extra_data(extra_data_dir_shot,extra_data_hair_pass_info,'lookdiff_3_hair_info.json')
    except Exception as e:
        print(traceback.format_exc())
        json_data = traceback.format_exc()

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: mayapy update_shot_lookdiff_3_hair_info.py <maya_file> <start_frame> <end_frame>')
        sys.exit(1)
    maya_file = sys.argv[1]
    start_frame = float(sys.argv[2])
    end_frame = float(sys.argv[3])
    main(maya_file, start_frame, end_frame)