# -*- coding:utf-8 -*-

from xml.etree import ElementTree
import os

def get_assets_angle(scene_xml_path):
    tree = ElementTree.parse(scene_xml_path)
    root = tree.getroot()

    l_instances = root.getiterator("instance")

    d_assets = {}
    for instance in l_instances:
        if instance.attrib.has_key('refFile'):
            asset = instance.attrib['refFile'].split('/')[-1].replace('.xml', '')
            i_attribs = instance.getiterator('attribute')
            viewable = False
            angle = 0.0
            for attr in i_attribs:
                if attr.attrib.has_key('name') and attr.attrib['name'] == 'viewable' and attr.attrib['value'] == 'yes':
                    viewable = True
                if attr.attrib.has_key('name') and attr.attrib['name'] == 'angle':
                    angle = float(attr.attrib['value'])

            if viewable:
                if not d_assets.has_key(asset):
                    d_assets[asset] = []
                d_assets[asset].append(angle)

    return d_assets


def get_assets_cnt(scene_xml_path):
    tree = ElementTree.parse(scene_xml_path)
    root = tree.getroot()

    l_instances = root.getiterator("instance")

    d_assets = {}
    for instance in l_instances:
        if instance.attrib.has_key('refFile'):
            asset = instance.attrib['refFile'].split('/')[-1].replace('.xml', '')
            asset=asset.split(".")[-1].rstrip("1234567890")
            i_attribs = instance.getiterator('attribute')
            viewable = False
            full_path = ''
            for attr in i_attribs:
                if attr.attrib.has_key('name') and attr.attrib['name'] == 'viewable' and attr.attrib['value'] == 'yes':
                    viewable = True
                if attr.attrib.has_key('name') and attr.attrib['name'] == 'fullPath':
                    full_path = attr.attrib['value']

            if full_path == '':
                continue

            if not d_assets.has_key(asset):
                d_assets[asset] = {'path':full_path, 'cnt':0, 'viewable':0, 'hidden':0}

            d_assets[asset]['cnt'] += 1
            if viewable:
                d_assets[asset]['viewable'] += 1
            else:
                d_assets[asset]['hidden'] += 1

    return d_assets


def get_assets(scene_xml_path, viewable_only=False):
    d_assets_cnt = get_assets_cnt(scene_xml_path)
    d_assets = {}

    for asset in d_assets_cnt.keys():
        if d_assets_cnt[asset]['viewable'] > 1 or (not viewable_only):
            d_assets[asset] = d_assets_cnt[asset]['path']

    return d_assets


def get_viewable_assets(scene_xml_path):
    return get_assets(scene_xml_path, viewable_only=True)


def get_cam_angle(scene_xml_path):
    tree = ElementTree.parse(scene_xml_path)
    root = tree.getroot()

    l_instances = root.getiterator("instance")
    for i in l_instances:
        if i.attrib['name'] == 'assets':
            for c in i.getchildren():
                if c.tag == 'cam_angle':
                    return float(c.attrib['value'])

    return None


def get_ani_assets(ani_xml_path):
    l_ani_assets = []
    if os.path.isfile(ani_xml_path):
        tree = ElementTree.parse(ani_xml_path)
        root = tree.getroot()

        l_assets = root.getiterator('asset')
        for asset in l_assets:
            if asset.attrib['status'] in ['animated', 'constrained']:
                l_ani_assets.append(asset.attrib['name'])

    return l_ani_assets

