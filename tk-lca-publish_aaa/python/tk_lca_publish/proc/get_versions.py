# -*- coding:utf-8 -*-

########################################################################################
#
# Author: liangyue
#
# Date: 2026.06
#
# Description:
#
########################################################################################

from production.shotgun_connection import Connection
sg = Connection('get_project_info').get_sg()


def get_task_versions(project_name, asset_name, task_name, type='Downstream'):
    """
    查询指定 asset/task 下的 Version 列表

    :param project_name: 项目名
    :param asset_name: asset名称
    :param task_name: task名称
    :param type: Version状态，可选
    :return: version list
    """

    project = sg.find_one(
        'Project',
        [['name', 'is', project_name]],
        []
    )

    if not project:
        return []

    filters = [
        ['project', 'is', project],
        ['entity.Asset.code', 'is', asset_name],
        ['sg_task.Task.step', 'name_is', task_name],
        ['sg_status_list', 'is_not', 'omt']
    ]

    # type过滤
    if type:
        filters.append(
            ['sg_version_type', 'is', type]
        )

    versions = sg.find(
        'Version',
        filters,
        [
            'code',
            'sg_path_to_movie',
            'sg_status_list',
            'created_at',
            'user',
            'sg_task',
            'tag_list'
        ],
        order=[
            {
                'field_name': 'created_at',
                'direction': 'desc'
            }
        ]
    )

    return versions


'''
versions = get_task_versions(
    'XUN',
    'td_test_labourer_e',
    'cfx',
    'Downstream'
)

'''

