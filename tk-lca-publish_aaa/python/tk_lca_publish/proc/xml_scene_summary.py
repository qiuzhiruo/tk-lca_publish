# -*- coding:utf-8 -*-

import proc.parse_shot_xml as parser
reload(parser)

def num_format( n):
    if n <100000000:
        return u'%.2f万' % (n/10000.0)
    else:
        return u'%.2f亿' % (n/100000000.0)

def summarize(scene_xml_path, sg, project, d_assets):
    d_assets_cnt = parser.get_assets_cnt(scene_xml_path)
    d_scene_description = {}
    face_cnt = 0
    for asset_name in d_assets_cnt.keys():
        if not d_assets.has_key(asset_name):
            d_assets[asset_name] = sg.find_one('Asset', [['code', 'is', asset_name], ['project', 'is', project]], ['sg_poly_count_hi', 'sg_asset_type'])

        asset = d_assets[asset_name]
        if asset is None or asset['sg_asset_type'] is None or asset['sg_asset_type'] == '':
            continue

        a_type = asset['sg_asset_type']
        if asset['sg_poly_count_hi'] is None:
            mesh_cnt = 0
        else:
            mesh_cnt = asset['sg_poly_count_hi']

        if not d_scene_description.has_key(a_type):
            d_scene_description[a_type] = {'total':0, 'viewable':0, 'mesh_cnt':0}

        d_scene_description[a_type]['viewable'] += d_assets_cnt[asset_name]['viewable']
        d_scene_description[a_type]['total'] += d_assets_cnt[asset_name]['viewable'] + d_assets_cnt[asset_name]['hidden']
        d_scene_description[a_type]['mesh_cnt'] += d_assets_cnt[asset_name]['viewable'] * mesh_cnt

    all_viewable = 0
    all_total = 0
    all_mesh_cnt = 0 
    txt = u'场景描述: 资产类别 可见资产数 总资产数 可见面数\n'
    for a_type in sorted(d_scene_description.keys()):
        txt += a_type + ': ' + str(d_scene_description[a_type]['viewable']) + ', ' + str(d_scene_description[a_type]['total']) + ', ' + num_format(d_scene_description[a_type]['mesh_cnt']) + '\n'
        all_viewable += d_scene_description[a_type]['viewable']
        all_total += d_scene_description[a_type]['total']
        all_mesh_cnt += d_scene_description[a_type]['mesh_cnt']

    txt += 'all: ' + str(all_viewable) + ', ' + str(all_total) + ', ' + num_format(all_mesh_cnt) + '\n'

    return txt
