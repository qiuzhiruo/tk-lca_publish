# -*- coding: utf-8 -*-


import os
import sys
import glob
import json
import maya.cmds as mc
import maya.cmds as cmds
import maya.standalone as standalone
from production.pipeline.pass_info import combine_pass_image, sg_pass_info
from production.feishu_utils import lca_feishu
from production.shotgun_connection import Connection
sg = Connection('get_project_info').get_sg()


try:
    import maya.standalone
    maya.standalone.initialize()
    maya.standalone.initialize(name='python')
except:
    pass


def main(preview_dir, project_name, asset_name, task_name, asset_step, user_name):
    body_folder = os.path.join(preview_dir, "tmp", "body_cam_body_cam")
    pattern = os.path.join(body_folder, "*.png")
    body_path_list = glob.glob(pattern)

    head_folder = os.path.join(preview_dir, "tmp", "head_cam_head_cam")
    pattern = os.path.join(head_folder, "*.png")
    head_path_list = glob.glob(pattern)

    combined_head_png = os.path.join(preview_dir, "combined_head.png")
    combined_all_png = os.path.join(preview_dir, "combined_all.png")
    # 合并图
    combine_pass_image.main(head_path_list, combined_head_png)
    combine_pass_image.main(body_path_list + head_path_list, combined_all_png)

    sg_pass = sg_pass_info.SGPassInfo(project_name, asset_name, task_name, asset_step)
    sg_pass.batch_create_pass(head_path_list)

    # 发布合并图
    # sg_pass.publish_combined_image(combined_head_png)
    sg_pass.publish_combined_image(combined_all_png)

    send_massage(project_name, asset_name, user_name)


def send_massage(proj, asset_name, art):
    project_id = 0
    asset_id = 0
    latest_version_id = 0
    projects = sg.find('Project', [['name', 'is', proj]], ['id'])
    if projects:
        project = projects[0]
        assets = sg.find('Asset',
                         [['project', 'is', project],
                          ['code', 'is', asset_name]],
                         ['id'])
        if assets:
            asset = assets[0]
            asset_id = asset['id']
            versions = sg.find('Version',
                               [['project', 'is', project],
                                ['entity', 'is', asset]],
                               ['id'],
                               [{'field_name': 'created_at', 'direction': 'desc'}],
                               limit=1)
            if versions:
                latest_version_id = versions[0]['id']
                project_id = project['id']

    web_path = 'https://smk.zhuiguang.com/projects/{}/version/{}'.format(project_id, latest_version_id)

    sed_person = get_preson_list(art)
    message_content = u"\n\n"

    message_content += u"艺术家:{}".format(art) + "\n"
    message_content += u"项目:{}".format(proj) + "\n"
    message_content += u"资产:{}".format(asset_name) + "\n"

    message_content += u"\n跳转到效果图:" + "\n"
    message_content += web_path + "\n\n"

    title_content = u'facePass 随机组合预览渲染完成'

    lca_feishu.main(to_user_list=sed_person, title=title_content, message=message_content, app='sunmark')



def get_preson_list(art):
    td_name_list = ["wangqi2", "zhenlin", "pangxuan"]
    lead_name_list = ["liyidong", "yangbin", "zhangyan", "yiyao", "aries", "liyao"]

    # 获取所有 pmd 名单
    pmd_people = sg.find('HumanUser', [['department.Department.code', 'in', ['pmd']],
                                       ['sg_status_list', 'is', 'act']], ['login'])
    pmd_name_list = []
    for person in pmd_people:
        pmd_name_list.append(person['login'])
    result = list(set(td_name_list + lead_name_list + pmd_name_list + [art]))
    return result



if __name__ == "__main__":
    path = sys.argv[1]
    proj_name = sys.argv[2]
    asset_name = sys.argv[3]
    task_name = sys.argv[4]
    asset_step = sys.argv[5]
    user_name = sys.argv[6]
    main(path, proj_name, asset_name, task_name, asset_step, user_name)