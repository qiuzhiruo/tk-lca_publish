# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.04
#
############################################

import os
from xml.etree import ElementTree

def get_stages():
    file_dir = os.path.dirname(__file__.replace('\\', '/'))
    xml_path = '/'.join(file_dir.split('/')[:-1]) + "/task_stages.xml"

    if not os.path.isfile(xml_path):
        print 'Failed to find stage setting file:', xml_path
        return []

    f = open(xml_path, 'r')
    xml_text = f.read()
    f.close()

    root = ElementTree.fromstring(xml_text)

    l_stage_nodes = root.getiterator("stage")
    l_stages = []
    for node in l_stage_nodes:
        l_tags = [tag.attrib['name'] for tag in node.getiterator("tag")]
        l_stages.append([node.attrib['step'], node.attrib['entity'], node.attrib['type'], node.attrib['task'], l_tags])

    return l_stages


