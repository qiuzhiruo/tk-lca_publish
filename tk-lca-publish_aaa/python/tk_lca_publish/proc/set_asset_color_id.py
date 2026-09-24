# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yu Huazhuo
#
# Date: 2017.03
#
# Description:
#
############################################


import os
import sys
import optparse
import random
import copy

if sys.platform.startswith('win'):
    SERVER_ROOT = 'Z:'
    # WORK_ROOT = 'W:/'
    # TOOL_ROOT = 'U:/'
    PUBLIC_ROOT = 'P:/'
elif sys.platform.startswith('linux'):
    SERVER_ROOT = '/mnt/proj'
    # WORK_ROOT = '/mnt/work/'
    # TOOL_ROOT = '/mnt/utility/'
    PUBLIC_ROOT = '/mnt/public/'
elif sys.platform.startswith('darwin'):
    SERVER_ROOT = '/Volumes/lcadata'
    # WORK_ROOT = '/Volumes/work/'
    # TOOL_ROOT = '/Volumes/utility/'
    PUBLIC_ROOT = '/Volumes/public/'

WORK_ROOT = os.getenv('LC_WORK')
TOOL_ROOT = os.getenv('LC_UTILITY')

d_assets_orig = {'chr':{'color':[(25, 50), (1 , 20), (1 , 20)], 'assets':{}, 'id_list':[]},
                 'crd':{'color':[(25, 50), (1 , 20), (1 , 20)], 'assets':{}, 'id_list':[]},
                 'asm':{'color':[(25, 50), (1 , 20), (1 , 20)], 'assets':{}, 'id_list':[]},
                 'prp':{'color':[(20, 50), (10, 40), (1 , 30)], 'assets':{}, 'id_list':[]},
                 'env':{'color':[(1 , 20), (1 , 20), (25, 50)], 'assets':{}, 'id_list':[]},
                 'veh':{'color':[(40, 50), (40, 50), (1 , 10)], 'assets':{}, 'id_list':[]},
                 'flg':{'color':[(1 , 20), (25, 50), (1 , 20)], 'assets':{}, 'id_list':[]}
                }

def get_sg():
    import production.shotgun_connection as shotgun_connection
    c = shotgun_connection.Connection('get_project_info')
    return c.get_sg()


def valid_color_id(asset):
    if isinstance(asset['sg_color_id'], (str, unicode)):
        tokens = asset['sg_color_id'].split(' ')
        if len(tokens) == 3 and tokens[0].isdigit() and tokens[1].isdigit() and tokens[2].isdigit():
            return True
    return False


def get_color_id(proj_name, asset_name, sg=None):
    if sg is None:
        sg = get_sg()

    asset_color_id = "0 0 0"
    proj_name = proj_name.upper()
    proj = sg.find_one('Project', [['name', 'is', proj_name]], [])

    if proj is None:
        print u'找不到项目:', proj_name
        return asset_color_id

    asset = sg.find_one('Asset', [['project', 'is', proj],['code','is',asset_name]], ['sg_asset_type', 'code', 'sg_color_id'])
    if asset is None:
        print u'找不到资产:', asset_name
        return asset_color_id

    if valid_color_id(asset):
        return asset['sg_color_id']
    else:
        return set_color_id(proj_name, asset_name=asset_name, sg=sg)


def set_color_id(proj_name, asset_name='', sg=None):

    if sg is None:
        sg = get_sg()

    asset_color_id = "0 0 0"
    proj_name = proj_name.upper()
    proj = sg.find_one('Project', [['name', 'is', proj_name]], [])

    if proj is None:
        print u'找不到项目:', proj_name
        return asset_color_id

    d_assets = copy.deepcopy(d_assets_orig)

    # Collect assets
    l_existing_id = []
    for asset in sg.find('Asset', [['project', 'is', proj]], ['sg_asset_type', 'code', 'sg_color_id']):
        if valid_color_id(asset):
            l_existing_id.append(asset['sg_color_id'])
            continue

        if asset['sg_asset_type'] is None or asset['code'] is None:
            continue

        a_type = asset['sg_asset_type']
        if not d_assets.has_key(a_type):
            continue

        d_assets[a_type]['assets'][asset['code']] = asset

    if asset_name != '':
        asset = sg.find_one('Asset', [['project', 'is', proj],['code','is',asset_name]], ['sg_asset_type', 'code', 'sg_color_id'])
        if asset is None:
            print u'找不到资产:', asset_name
            return asset_color_id

        a_type=asset['sg_asset_type']
        if not d_assets.has_key(a_type):
            return asset_color_id

        if not d_assets[a_type]['assets'].has_key(asset_name):
            return asset['sg_color_id']

        d_assets = {a_type:copy.deepcopy(d_assets_orig[a_type])}
        d_assets[a_type]['assets'][asset_name] = asset

    # Build color id list
    for a_type in d_assets.keys():
        for x in range(d_assets[a_type]['color'][0][0], d_assets[a_type]['color'][0][1]+1):
            for y in range(d_assets[a_type]['color'][1][0], d_assets[a_type]['color'][1][1]+1):
                for z in range(d_assets[a_type]['color'][2][0], d_assets[a_type]['color'][2][1]+1):
                    color_id = '%s %s %s' % (x*5, y*5, z*5)

                    if not color_id in l_existing_id:
                        d_assets[a_type]['id_list'].append(color_id)

        if len(d_assets[a_type]['assets'].keys()) > len(d_assets[a_type]['id_list']):
            print 'Error: cant assign %s availabe color ids to %s %s assets' % (len(d_assets[a_type]['id_list']), len(d_assets[a_type]['assets'].keys()), a_type)
            continue

        for a_name in sorted(d_assets[a_type]['assets'].keys()):
            asset = d_assets[a_type]['assets'][a_name]
            i = random.randint(1, len(d_assets[a_type]['id_list'])) - 1
            color_id = d_assets[a_type]['id_list'].pop(i)
            l_existing_id.append(color_id)
            print '    Set color id:', a_type, a_name, color_id
            sg.update('Asset', asset['id'], {'sg_color_id':color_id})

            if asset_name == a_name:
                asset_color_id = color_id

    return asset_color_id


#if __name__ == "__main__":
#     print set_color_id('tst')
