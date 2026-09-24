# -*-coding:utf-8 -*-
import traceback
import maya.cmds as cmds
import sys
import os

#sys.path.append('/mnt/utility/toolset/lib/production')
from production.shotgun_connection import Connection

# 全局初始化 Shotgun 连接
def initialize_sg():
    try:
        return Connection('get_project_info').get_sg()
    except Exception as e:
        cmds.warning("Shotgun 初始化失败: %s" % str(e))
        return None

sg = initialize_sg()

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"当前镜头by_shot是否添加"
        self.description = u"镜头下如果有by_shot任务需要等待by_shot完成后并且添加到当前文件中"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

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

    def has_by_shot_grp(self):
        cmds.objExists('assets')
        children = cmds.listRelatives('assets', children = True) or []

        lay_grp = [child for child in children if cmds.objectType(child) == "transform"
                  and child.lower() == "lay"]
        grand_children = cmds.listRelatives(lay_grp[0], children=True, fullPath=True) or []
        # 查找包含'by_shot'的组
        for obj in grand_children:
            if cmds.objectType(obj) == "transform" and "by_shot" in obj.lower():
                print(u"找到符合的组: {}".format(obj))
                return True

        return False


    def run_check(self):
        by_shot_grp = self.has_by_shot_grp()
        found_tasks = self.get_task()
        has_task, by_shot_task  = self.has_by_shot_task(found_tasks)
        if not has_task:
            return ""
        status = by_shot_task['sg_status_list'].lower().strip()

        if status == "da" and by_shot_grp:
            return ''
        elif not by_shot_grp and status == "da":
            return u'当前镜头by_shot已完成，请使用工具添加by_shot'
        else:
            return u'镜头的by_shot任务状态为：{},需要等by_shot制作完成才能趴下游'.format(status)



    def run_fix(self):
        return self.run_fix

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
