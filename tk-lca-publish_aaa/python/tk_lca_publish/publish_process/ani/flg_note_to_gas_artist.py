# -*- coding:utf-8 -*-

import os,sys
import traceback
import shutil

import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as om2

import xml.dom.minidom as minidom

def main(dialog):
    info = dialog.sg.find_one('Task', [['project', 'name_is', dialog.project['name'].lower()],
                                            ['id', 'is', dialog.task['id']]], ['sg_status_list'])
    if not info: return ""

    links = []
    links.append(dialog.entity)
    # subject = u'%s 提交了 %s 的新版动画' % (
    #     dialog.user['name'],
    #     dialog.entity['name']
    # )
    subject = u'通知 GAS 组：%s 有一些 flg 资产 是 <显示状态>/<在帧范围内位移了>' % dialog.entity['name']

    users = ''
    users = dialog.sg.find(
            'HumanUser',
            [{'filter_operator': 'all',
                'filters': [['department','name_contains','Gas']]}]
        )
    description=None
    # description_default = u'Note 逻辑描述:\n如果镜头文件内 存在 flg 组,列出 flg 组下 flg 单体的 显示&位移 情况\n如果镜头文件内 存在 plt_proxy_grp 组,列出 plt_proxy_grp 组下 flg 单体的 显示&位移 情况\n'
    description_default = ''
    flg_grp_note_str,plt_proxy_grp_note_str = get_description()
    if flg_grp_note_str and not plt_proxy_grp_note_str:
        description = description_default+flg_grp_note_str
    elif not flg_grp_note_str and plt_proxy_grp_note_str:
        description = description_default+plt_proxy_grp_note_str
    elif flg_grp_note_str and plt_proxy_grp_note_str:
        description = description_default+flg_grp_note_str+'\n'+plt_proxy_grp_note_str
    if description:
        # 'addressings_to': users,
        note = dialog.sg.create(
            'Note',
            {'user': dialog.user,
                'content': description,
                'subject': subject,
                'project': dialog.project,
                'note_links': links,
                'sg_note_type': u'通知',
                'tasks': [dialog.task]},
        )

    return ""

# 获取 node 显示情况,在帧范围内,是一直显示,还是有key帧显示
def get_vis(node,start_frame,end_frame):
    if 'visibility' in cmds.listAttr(node):
        node_vis_attr = node+'.visibility'
        # 获取 node visibility 的 父级连接，看是否是 key 帧
        node_parent = cmds.listConnections(node_vis_attr,s=1,d=0,p=1) # [u'flg_visibility.output']
        # 有 父级连接
        if node_parent:
            # 获取 node visibility 的 父级连接 是 animCurve 类型，用来判定是否有 key 帧
            node_parent_keyType = list(set([i for i in node_parent if 'animCurve' in str(pm.nodeType(i))]))
            if node_parent_keyType!=[]:
                # 返回当前 镜头 起始结束帧 之内 node visibility 的 key 帧
                node_vis_keyFrames = cmds.keyframe(node_vis_attr,q=1,ev=0) # [18.0, 55.0]
                node_vis_keyFrames_new = [i for i in node_vis_keyFrames if i >= start_frame and i <= end_frame] # [55.0]
                # print node_vis_keyFrames_new # [1001.0, 1016.0]
                # 如果 当前 镜头 起始结束帧 之内 node visibility 没有 key 帧
                if len(node_vis_keyFrames_new)==0:
                    # 此时 获取 镜头 起始帧的 node visibility 值
                    keyFrame_value = cmds.getAttr(node_vis_attr,time=start_frame)
                    return keyFrame_value
                # 如果 当前 镜头 起始结束帧 之内 node visibility 有 一个key 帧
                if len(node_vis_keyFrames_new)==1:
                    # 此时 获取 镜头 起始帧的 node visibility 值
                    keyFrame_value = cmds.getAttr(node_vis_attr,time=node_vis_keyFrames_new[0])
                    return keyFrame_value
                # 如果 当前 镜头 起始结束帧 之内 node visibility 有 多个key 帧
                if len(node_vis_keyFrames_new)>1:
                    keyFrame_value_list = [cmds.getAttr(node_vis_attr,time=keyFrame) for keyFrame in node_vis_keyFrames_new]
                    # print len(list(set(keyFrame_value_list)))
                    if len(list(set(keyFrame_value_list))) == 1:
                        return list(set(keyFrame_value_list))[0]
                    else:
                        keyFrame_str = ''
                        # 此时 获取 shot 内每一个 key 帧的数值
                        for keyFrame in node_vis_keyFrames_new:
                            keyFrame_value = cmds.getAttr(node_vis_attr,time=keyFrame)
                            keyFrame_str = keyFrame_str + str(keyFrame)+':'+str(keyFrame_value)+' '
                        return keyFrame_str # 1001.0:False 1016.0:True 
            else:
                return cmds.getAttr(node_vis_attr)
        else:
            return cmds.getAttr(node_vis_attr)
    else:
        return
# 获取 plt_proxy_grp 的 xform,判定是否位移了
def get_plt_proxy_grp_xform(node):
    assets_grp = 'assets'
    assets_xform_inv = cmds.getAttr(assets_grp+'.inverseMatrix')
    m1=om2.MMatrix(assets_xform_inv)

    node_xform = pm.xform(node,q=True,matrix=True,worldSpace=True)
    m2=om2.MMatrix(node_xform)
    #print type(m1*m2)
    #print type((((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))))
    if m1*m2!=om2.MMatrix([1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]):
        return str(node_xform)
    else:
        return None
# 获取 plt_proxy_grp 下的 组 的 xform,判定是否位移了
def get_grp_xform(node):
    node_xform = pm.xform(node,q=True,matrix=True,worldSpace=True)
    if node_xform!=[1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]:
        return node_xform
    else:
        return
# 获取 plt_proxy_grp 下的 ar 的 xform
def get_ar_xform(node):
    node_name = node[:-3]
    node_mesh_grp = node+'|%s:master|%s:poly|%s:hi|%s:mesh_grp' % (node_name,node_name,node_name,node_name)
    if cmds.objExists(node_mesh_grp):
        node_xform = pm.xform(node_mesh_grp,q=True,matrix=True,worldSpace=True)
        return node_xform
    else:
        node_xform = pm.xform(node,q=True,matrix=True,worldSpace=True)
        return node_xform

# 获取 flg 组下 单体的 xform 信息
def get_flg_ar_xform(node):
    node_name = node.split('|')[-1][:-3]
    # print node_name
    node_mesh_grp = node+'|%s:master|%s:poly|%s:hi|%s:mesh_grp' % (node_name,node_name,node_name,node_name)
    # print node_mesh_grp,cmds.objExists(node_mesh_grp)
    if cmds.objExists(node_mesh_grp):
        node_xform = pm.xform(node_mesh_grp,q=True,matrix=True,worldSpace=True)
        return 'mesh_grp_xform:'+str(node_xform)
    else:
        node_xform = pm.xform(node,q=True,matrix=True,worldSpace=True)
        return 'ar_xform:'+str(node_xform)

# 获取 flg 组,及其组下单体的 显示&位移情况
def get_flg_grp_vis_str(all_assemblyReference_nodes):
    start_frame = pm.playbackOptions(query = True, minTime = True)
    end_frame = pm.playbackOptions(query = True, maxTime = True)
    # print '-'*80
    flg_grp_note_str = ''
    # 针对 flg 组
    flg_grp = '|assets|flg'
    # flg_grp_note_str = flg_grp_note_str + flg_grp + ' '
    # 如果 flg 组 存在
    if cmds.objExists(flg_grp):
        # flg_grp_note_str = flg_grp_note_str + u'存在,'
        flg_grp_vis = get_vis(flg_grp,start_frame,end_frame)
        # 如果 flg 组 显示
        if flg_grp_vis:
            # 判定 flg 组 显示 情况，是一直显示，还是有显示有隐藏
            # # 如果 有显示，有隐藏 情况
            # if type(flg_grp_vis) is str:
            #     flg_grp_note_str = flg_grp_note_str + u'且在 帧范围 内 一段帧是隐藏状态，一段帧是显示状态 >> 具体 显示/隐藏 key 帧情况 如下(False 代表隐藏,True 代表显示):\n'+flg_grp+' > {'+flg_grp_vis[:-1]+'}\n'
            # # 如果 一直显示 情况
            # if type(flg_grp_vis) is bool:
            #     flg_grp_note_str = flg_grp_note_str + u'且在 帧范围 内 一直是显示状态：\n'
            # 获取 flg 下的 子资产
            flg_assemblyReference_nodes = [i for i in all_assemblyReference_nodes if flg_grp in i]
            # 如果 flg 下有子资产
            if flg_assemblyReference_nodes!=[]:
                flg_assemblyReference_nodes_num = len(flg_assemblyReference_nodes)
                # flg_grp_note_str = flg_grp_note_str + (u'%s 下面总计有 %s 个 单体,' % (flg_grp,str(flg_assemblyReference_nodes_num)))
                flg_grp_note_str = flg_grp_note_str+flg_grp+'>>>\n'
                # 获取 flg 下子资产的 各个 显示状态
                flg_assemblyReference_node_vis_list = []
                for flg_assemblyReference_node in flg_assemblyReference_nodes:
                    flg_assemblyReference_node_vis = get_vis(flg_assemblyReference_node,start_frame,end_frame)
                    flg_assemblyReference_node_vis_list.append(flg_assemblyReference_node_vis)
                # print flg_assemblyReference_node_vis_list,len(list(set(flg_assemblyReference_node_vis_list))) # [True, False, '1001.0:True 1016.0:False ', True, True, True, True] 3
                # 如果 flg 下子资产 只有一种显示状态
                if len(list(set(flg_assemblyReference_node_vis_list))) == 1:
                    # 如果 子资产 显示状态 都 为 显示
                    if list(set(flg_assemblyReference_node_vis_list))[0]:
                        # flg_grp_note_str = flg_grp_note_str + u'且在 帧范围 内 全部单体 一直是显示状态(标签为隐藏状态的单体此处忽略)：\n'
                        flg_assemblyReference_node_rep_list = []
                        for flg_assemblyReference_node in flg_assemblyReference_nodes:
                            activeLabel = pm.assembly(flg_assemblyReference_node, q=1, activeLabel=1)
                            # 如果 子资产 标签 不为 None，locator
                            if activeLabel!='' and '.locator' not in activeLabel:
                                flg_assemblyReference_node_rep_list.append(flg_assemblyReference_node)
                                flg_assemblyReference_node_xform = get_flg_ar_xform(flg_assemblyReference_node)
                                flg_grp_note_str = flg_grp_note_str + flg_assemblyReference_node +' > {' + u'一直显示} > '+activeLabel+u' > 默认是位移了的 '+flg_assemblyReference_node_xform+'\n'
                        # 如果 显示的 子资产 标签 都为 None，locator
                        if flg_assemblyReference_node_rep_list==[]:
                            flg_grp_note_str = None
                    else:
                        flg_grp_note_str = None
                # 如果 flg 下子资产 有多种显示状态
                else:
                    flg_grp_note_str = flg_grp_note_str + u'且在 帧范围 内 部分单体 一段帧是隐藏状态，一段帧是显示状态(一直是隐藏的单体此处忽略):\n具体 显示/隐藏 key 帧情况 如下(False 代表隐藏,True 代表显示):\n'
                    flg_assemblyReference_node_rep_list = []
                    for flg_assemblyReference_node in flg_assemblyReference_nodes:
                        flg_assemblyReference_node_vis = get_vis(flg_assemblyReference_node,start_frame,end_frame)
                        # 如果 子资产 某个 为 有显示，又隐藏 状态
                        if type(flg_assemblyReference_node_vis) is str:
                            activeLabel = pm.assembly(flg_assemblyReference_node, q=1, activeLabel=1)
                            # 如果 子资产 标签 不为 None，locator
                            if activeLabel!='' and '.locator' not in activeLabel:
                                flg_assemblyReference_node_rep_list.append(flg_assemblyReference_node)
                                flg_assemblyReference_node_xform = get_flg_ar_xform(flg_assemblyReference_node)
                                flg_grp_note_str = flg_grp_note_str + flg_assemblyReference_node +' > {'+flg_assemblyReference_node_vis[:-1]+'} > '+activeLabel+u' > 默认是位移了的 '+flg_assemblyReference_node_xform+'\n'
                        # 如果 子资产 某个 为 一直显示 状态
                        if type(flg_assemblyReference_node_vis) is bool:
                            activeLabel = pm.assembly(flg_assemblyReference_node, q=1, activeLabel=1)
                            # 如果 子资产 标签 不为 None，locator
                            if flg_assemblyReference_node_vis and activeLabel!='' and '.locator' not in activeLabel:
                                flg_assemblyReference_node_rep_list.append(flg_assemblyReference_node)
                                flg_assemblyReference_node_xform = get_flg_ar_xform(flg_assemblyReference_node)
                                flg_grp_note_str = flg_grp_note_str + flg_assemblyReference_node +' > {' + u'一直显示} > '+activeLabel+u' > 默认是位移了的 '+flg_assemblyReference_node_xform+'\n'
                    # 如果 显示的 子资产 标签 都为 None，locator
                    if flg_assemblyReference_node_rep_list==[]:
                        flg_grp_note_str = None
            else:
                flg_grp_note_str = None
        else:
            flg_grp_note_str = None
    else:
        flg_grp_note_str = None
    return flg_grp_note_str
# 获取 plt_proxy_grp 下的 ar 的 xform,以及 asb xml 内记录的 ar 的 xform 信息
def get_ar_xml_xform(node,instance_nodes):
    node_name = node.split(':')[-1].split('_AR')[0]
    if not instance_nodes:
        raise Exception('该node 无instance_nodes 信息,请检查其asb模型scene_graph_xml是否完整: {}'.format(node))
    new_xml_xform = ''
    new_node_xform = ''
    for instance_node in instance_nodes:
        if instance_node.getAttribute('name') == node_name:

            xml_xform = instance_node.childNodes[3].getAttribute('value')
            new_xml_xform = [round(float(i),6) for i in xml_xform.split(' ')]

            node_xform = get_ar_xform(node)
            new_node_xform = [round(float(i),6) for i in node_xform]

            return new_xml_xform,new_node_xform
    
    return new_xml_xform,new_node_xform

# 获取 plt_proxy_grp 组下单体的 显示&位移情况
def get_grp_vis_str(grp_node,grp_vis_str,start_frame,end_frame,instance_nodes,grp_vix):
    # 是组
    if grp_node.endswith('_grp'):
        grp_node_vis = get_vis(grp_node,start_frame,end_frame)
        # 如果 grp_node 组 显示
        if grp_node_vis:
            new_grp_vis_str = ''
            # new_grp_vis_str = grp_vis_str + grp_node + ' '
            # 判定 grp_node 组 显示 情况，是一直显示，还是有显示有隐藏
            # # 如果 有显示，有隐藏 情况
            # if type(grp_node_vis) is str:
            #     new_grp_vis_str = new_grp_vis_str + u'在 帧范围 内 一段帧是隐藏状态，一段帧是显示状态 >> 具体 显示/隐藏 key 帧情况 如下(False 代表隐藏,True 代表显示):\n'+grp_node+' > {'+grp_node_vis[:-1]+'}\n'
            # # 如果 一直显示 情况
            # if type(grp_node_vis) is bool:
            #     new_grp_vis_str = new_grp_vis_str + u'在 帧范围 内 一直是显示状态：\n'
            # grp_node_xform = get_grp_xform(grp_node)
            # # 如果 grp_node 位移了
            # if grp_node_xform:
            #     new_grp_vis_str = new_grp_vis_str + grp_node + u' > 位移了 grp_xform:'+str(grp_node_xform)+'\n'

            # 获取 grp_node 下一层级的 子资产
            grp_node_children = cmds.listRelatives(grp_node,children=1)
            if grp_node_children!=[]:
                
                new_grp_vix = 0 # 用于返回 组 下的单体是否有显示的,没有,就不写入 str 里面
                for grp_node_child in grp_node_children:
                    new_grp_vis_str,new_grp_vix = get_grp_vis_str(grp_node_child,new_grp_vis_str,start_frame,end_frame,instance_nodes,new_grp_vix)
                if new_grp_vix != 0:
                    grp_vis_str = new_grp_vis_str
                    grp_vix = new_grp_vix+grp_vix
            else:
                pass
        else:
            pass
    # 是 AR 节点
    if grp_node.endswith('_AR'):
        grp_node_vis = get_vis(grp_node,start_frame,end_frame)
        activeLabel = pm.assembly(grp_node, q=1, activeLabel=1)
        # 如果 node 标签 不为 None，locator
        if activeLabel!='' and '.locator' not in activeLabel:
            new_xml_xform,new_node_xform = get_ar_xml_xform(grp_node,instance_nodes)
            if new_xml_xform==new_node_xform:
                # node_vis_str = node_vis_str + '\n'
                pass
            else:
                # 如果 node 显示
                if grp_node_vis:
                    grp_vix = grp_vix+1 # 有显示 就 +1
                    node_vis_str = grp_vis_str + grp_node
                    # 如果 node 为 有显示，又隐藏 状态
                    if type(grp_node_vis) is str:
                        # print grp_node_vis
                        node_vis_str = node_vis_str +' > {'+grp_node_vis[:-1]+'} > '
                    # 如果 node 为 一直显示 状态
                    if type(grp_node_vis) is bool:
                        # print grp_node_vis
                        node_vis_str = node_vis_str +' > {' + u'一直显示} > '
                    node_vis_str = node_vis_str + activeLabel
                    node_vis_str = node_vis_str + u' > 在镜头内是位移了的 ar_xform:'+str(new_node_xform)+'\n'
                    grp_vis_str = node_vis_str
        else:
            pass
    
    return grp_vis_str,grp_vix

# 获取 plt_proxy_grp 组,及其组下单体的 显示&位移情况
def get_plt_proxy_grp_vis_str():
    start_frame = pm.playbackOptions(query = True, minTime = True)
    end_frame = pm.playbackOptions(query = True, maxTime = True)
    # print '-'*80
    flg_grp_note_str = ''
    # 针对 plt_proxy_grp 组
    flg_grp = '*:*:plt_proxy_grp'
    all_plt_proxy_grp = cmds.ls(flg_grp) # [u'b30_waibu_lanruosi_scn:waibu_lanruosi_asb:plt_proxy_grp']
    # 循环 每一个 plt_proxy_grp
    for plt_proxy_grp in all_plt_proxy_grp:
        plt_proxy_grp_str = ''
        # plt_proxy_grp_str = plt_proxy_grp_str + plt_proxy_grp + ' '
        # 如果 plt_proxy_grp 组 存在
        if cmds.objExists(plt_proxy_grp):
            # cmds.setAttr(plt_proxy_grp+'.inheritsTransform',0)
            # plt_proxy_grp_str = plt_proxy_grp_str + u'存在,'
            plt_proxy_grp_vis = get_vis(plt_proxy_grp,start_frame,end_frame)
            # 如果 plt_proxy_grp 组 显示
            if plt_proxy_grp_vis:
                # 判定 plt_proxy_grp 组 显示 情况，是一直显示，还是有显示有隐藏
                # # 如果 有显示，有隐藏 情况
                # if type(plt_proxy_grp_vis) is str:
                #     plt_proxy_grp_str = plt_proxy_grp_str + u'且在 帧范围 内 一段帧是隐藏状态，一段帧是显示状态 >> 具体 显示/隐藏 key 帧情况 如下(False 代表隐藏,True 代表显示):\n'+plt_proxy_grp+' > {'+plt_proxy_grp_vis[:-1]+'}\n'
                # # 如果 一直显示 情况
                # if type(plt_proxy_grp_vis) is bool:
                #     plt_proxy_grp_str = plt_proxy_grp_str + u'且在 帧范围 内 一直是显示状态：\n'
                # plt_proxy_grp_xform = get_plt_proxy_grp_xform(plt_proxy_grp)
                # # 如果 plt_proxy_grp 位移了
                # if plt_proxy_grp_xform:
                #     plt_proxy_grp_str = plt_proxy_grp_str + plt_proxy_grp + u' > 在镜头内是位移了的 grp_xform:'+plt_proxy_grp_xform+'\n\n'
                # else:
                #     plt_proxy_grp_str = plt_proxy_grp_str + '\n'
                
                # 获取 plt_proxy_grp 下一层级的 子资产
                plt_proxy_grp_children = cmds.listRelatives(plt_proxy_grp,children=1)
                if plt_proxy_grp_children!=[]:
                    # 此处先 返回 plt_proxy_grp 上层级的 asb 的 xml 路径,用于对比 plt_proxy_grp 下面的 单体是否位移
                    asb_node = plt_proxy_grp.split(':')[0]+':'+plt_proxy_grp.split(':')[1]+'_AR'
                    if cmds.objExists(asb_node):
                        asb_node_definition_path = cmds.getAttr(asb_node+'.definition').replace('\\','/')
                        asb_node_xml_path = asb_node_definition_path.replace('/assembly_definition/','/scene_graph_xml/')[:-3]+'.xml'
                        if sys.platform.startswith("win"):
                            asb_node_xml_path = 'Z:/projects/'+asb_node_xml_path.split('/projects/')[-1]
                        else:
                            asb_node_xml_path = '/mnt/proj/'+asb_node_xml_path.split('/proj/')[-1]
                        if os.path.exists(asb_node_xml_path):
                            print("asb_node_xml_path",asb_node_xml_path)
                            doc = minidom.Document()
                            xml_path = asb_node_xml_path
                            doml  = minidom.parse(xml_path)
                            root  = doml .documentElement
                            instance_nodes = root.getElementsByTagName('instance')
                            # 此处做此设置,更方便对比 plt_proxy_grp 下面的 单体是否位移
                            cmds.setAttr((plt_proxy_grp+'.inheritsTransform'),0)
                            grp_vis_str = ''# 用于返回 plt_proxy_grp 组 下的对象(组&单体)是否有显示的,没有,就不写入 str 里面
                            grp_vix = 0
                            # 循环 plt_proxy_grp 下面的 每一个对象,有可能是组,有可能就是AR
                            for plt_proxy_grp_child in plt_proxy_grp_children:
                            # plt_proxy_grp_child = 'b30_waibu_lanruosi_scn:waibu_lanruosi_asb:huang_geshu_d_grp'
                            # plt_proxy_grp_child = 'b30_waibu_lanruosi_scn:waibu_lanruosi_asb:hp_lanruosi_grass_a_flg11_AR'
                                grp_vis_str,grp_vix = get_grp_vis_str(plt_proxy_grp_child,grp_vis_str,start_frame,end_frame,instance_nodes,grp_vix)
                            if grp_vis_str:
                                plt_proxy_grp_str = plt_proxy_grp_str+'plt_proxy_grp >>>\n'
                                plt_proxy_grp_str = plt_proxy_grp_str+grp_vis_str
                            # print 'grp_vix >',grp_vix
                            if grp_vix==0:
                                plt_proxy_grp_str = None
                            # 对比结束 还原 设置
                            cmds.setAttr((plt_proxy_grp+'.inheritsTransform'),1)
                else:
                    plt_proxy_grp_str = None
            
            else:
                plt_proxy_grp_str = None
            # cmds.setAttr(plt_proxy_grp+'.inheritsTransform',1)
        else:
            plt_proxy_grp_str = None

        
        if flg_grp_note_str != None and plt_proxy_grp_str != None:
            flg_grp_note_str = flg_grp_note_str + plt_proxy_grp_str
        elif flg_grp_note_str == None and plt_proxy_grp_str != None:
            flg_grp_note_str = plt_proxy_grp_str
        elif flg_grp_note_str != None and plt_proxy_grp_str == None:
            flg_grp_note_str = flg_grp_note_str
        else:
            flg_grp_note_str = None
    
    return flg_grp_note_str

def get_description():
    
    # 先得到所有的 assemblyReference 节点
    all_assemblyReference_nodes = cmds.ls(allPaths=True, dag=True, l=True,type='assemblyReference')

    # 获取 flg 组,及其组下单体的 显示&位移情况
    # 显示 会发 note
    # 显示 并 位移 会发 note
    flg_grp_note_str = get_flg_grp_vis_str(all_assemblyReference_nodes)

    # 获取 plt_proxy_grp 组,及其组下单体的 显示&位移情况
    # 显示 会发 note
    # 显示 并 位移 会发 note
    plt_proxy_grp_note_str = get_plt_proxy_grp_vis_str()

    


    # print flg_grp_note_str
    # print plt_proxy_grp_note_str
    # print '-'*80
    
    return flg_grp_note_str,plt_proxy_grp_note_str


