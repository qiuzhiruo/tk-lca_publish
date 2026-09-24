# -*- coding:utf-8 -*-
import traceback
import os
import maya.cmds as cmds
import shutil  # 用于文件复制
import sys

# sys.path.append('/mnt/utility/toolset/lib/production')
from production.shotgun_connection import Connection

# 全局初始化 Shotgun 连接
def initialize_sg():
    try:
        return Connection('get_project_info').get_sg()
    except Exception as e:
        cmds.warning("Shotgun 初始化失败: %s" % str(e))
        return None

sg = initialize_sg()

# All publish process will use StdProcess as the class name.
class StdProcess():
    def get_task(self):
        """获取当前场景关联镜头下的任务信息"""
        # 获取当前场景路径
        scene_path = cmds.file(q=True, sceneName=True)
        if not scene_path:
            cmds.warning(u"场景未保存，请先保存场景")
            return []

        print scene_path
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

        # 从路径中提取项目名称和镜头代码
        proj_name = scene_path.split('/')[-8]
        filename = os.path.basename(scene_path)
        shot_code = filename.split('.')[0]
        print "____________!!!!!!!!!!!!!!!!"
        print u"项目名称: {}".format(proj_name)
        print u"镜头代码: {}".format(shot_code)
        print "____________!!!!!!!!!!!!!!!!"

        # 1. 查询镜头 (添加项目过滤)
        shot_filters = [
            ["project.Project.name", "is", proj_name],
            ["code", "is", shot_code]
        ]

        shot = sg.find_one("Shot", shot_filters, ["id", "code", "project"])

        if not shot:
            cmds.warning(u"未找到镜头: {} (项目: {})".format(shot_code, proj_name))
            return []

        print u"找到镜头 ID: {}".format(shot['id'])

        # 2. 查询所有任务 (模糊查询包含"by_shot"的任务)
        task_filters = [
            ["entity", "is", {"type": "Shot", "id": shot["id"]}],
            ["content", "contains", "by_shot"]
        ]

        tasks = sg.find("Task", task_filters, ["content", "sg_status_list"])

        # 返回任务列表
        return tasks

    def has_by_shot_task(self,tasks):
        """检查任务列表中是否有名为'by_shot'的任务"""
        if not tasks:
            return False, None

        # 精确查找任务名为"by_shot"的任务（忽略大小写）
        for task in tasks:
            if task.get('content', '').lower().strip() == "by_shot":
                return True, task


        # 如果没有找到精确匹配的任务
        return False, None

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"by_shot输出缓存"
        self.description = u"拷贝W盘中的by_shot缓存到Z盘路径下，并且替换场景中的AlembicNode节点的abc_file路径"
        return

    def copy_abc(self,cache_path):
        # 获取当前场景文件所在的目录
        current_file_path = cmds.file(q=True, sceneName=True) or ""
        # 提取Maya工作目录
        maya_dir = os.path.dirname(current_file_path)

        # 构建源文件路径 - 根据您描述的位置
        source_file = os.path.join(maya_dir, "by_shot", "input.abc")

        # 验证源文件是否存在
        if not os.path.exists(source_file):
            cmds.warning(u"找不到源ABC文件: {}".format(source_file))

        target_file = os.path.join(cache_path, "input.abc")

        try:
            # 复制并保留文件元数据（修改时间等）
            shutil.copy2(source_file, target_file)
            print(u"成功复制文件")
        except:
            cmds.warning(u"复制文件失败")

    def get_AlembicNode(self):
        # 获取 'by_shot_grp' 的所有直接子节点（变换节点）
        children = cmds.listRelatives('by_shot_grp', children=True) or []

        # 过滤掉以 _DEFAULT 或 _INS 结尾的节点
        filtered_children = [child for child in children if not child.endswith(('_DEFAULT', '_INS'))]

        # 存储所有关联的mesh节点
        all_mesh_nodes = []

        # 遍历每个过滤后的变换节点
        for transform in filtered_children:
            # 1. 获取直接关联的形状节点
            shapes = cmds.listRelatives(transform, shapes=True) or []

            # 2. 筛选出mesh类型的形状节点
            mesh_shapes = [s for s in shapes if cmds.objectType(s, isType="mesh")]

            # 3. 添加到结果列表
            all_mesh_nodes.extend(mesh_shapes)

        # print all_mesh_nodes

        node = cmds.listConnections(all_mesh_nodes)
        print node
        abc_node = [abc for abc in node if abc.endswith(('AlembicNode'))]
        print abc_node
        if abc_node:
            return abc_node[0]
        else:
            return None

    def replace_abc_file(self,new_abc_path):
        node_name = self.get_AlembicNode()
        new_path = new_abc_path
        try:
            # 1. 验证节点存在并类型正确
            if not cmds.objExists(node_name):
                raise RuntimeError(u"节点 {} 不存在".format(node_name))

            if cmds.nodeType(node_name) != "AlembicNode":
                raise RuntimeError(u"节点 {} 不是 AlembicNode 类型".format(node_name))

            # 2. 设置新路径
            attribute_name = "{}.abc_File".format(node_name)
            cmds.setAttr(attribute_name, new_path, type="string")

            # 3. 验证设置成功
            updated_path = cmds.getAttr(attribute_name)
            if isinstance(updated_path, list) and updated_path:
                updated_path = updated_path[0]
            if isinstance(updated_path, unicode):
                updated_path = updated_path.encode('utf-8')

            # 4. 打印结果
            print u"成功修改 Alembic 文件路径:"
            print u"节点: {}".format(node_name)
            print u"原路径: {}".format(updated_path)  # 这里显示更新后的路径

            # 5. 可选：检查路径是否一致
            if updated_path != new_path:
                print u"警告: 设置后的路径与目标路径不一致!"
                print u"设置的目标路径: {}".format(new_path)
                print u"实际返回的路径: {}".format(updated_path)
            else:
                print u"路径一致，修改成功!"

        except Exception as e:
            print u"无法修改文件路径: {}".format(str(e))
            # 打印更详细的错误信息
            import traceback
            traceback.print_exc()


    def proceed(self):
        found_tasks = self.get_task()
        has_task, by_shot_task = self.has_by_shot_task(found_tasks)
        if not has_task:
            return ""
        try:
            # 创建 ani 的版本文件夹
            self.dialog.version_dir = self.dialog.publish_root + '/' + self.dialog.version_name
            if not os.path.isdir(self.dialog.version_dir):
                os.makedirs(self.dialog.version_dir)

            by_shot_cache_dir = os.path.join(self.dialog.version_dir, 'by_shot_cache').replace('\\', '/')
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            print by_shot_cache_dir
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            if os.path.exists(by_shot_cache_dir):
                return by_shot_cache_dir
            else:
                try:
                    os.chmod(self.dialog.version_dir, 0777)
                except:
                    pass
                os.makedirs(by_shot_cache_dir)

            self.copy_abc(by_shot_cache_dir)

            acb_file = os.path.join(by_shot_cache_dir, "input.abc")
            self.replace_abc_file(acb_file)
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description