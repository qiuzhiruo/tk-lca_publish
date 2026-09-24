# -*- coding: utf-8 -*-
import os
import platform
import maya.cmds as cmds
import xml.etree.ElementTree as ET

# 定义你要查找的组名
grp_name = 'chr'

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"对比上一版xml和文件中的命名空间是否有变化"
        self.description = u"对比上一版文件中的xml记录的命名空间和当前文件中的资产命名空间是否发生了改变，增加和减少时允许的，但是不允许更改命名空间"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def xml_path(self):
        # 1. 获取场景路径
        full_path = cmds.file(query=True, sceneName=True)
        if not full_path:
            print u"请先保存或打开一个场景文件"
            return None
        sys_name = platform.system()



        if '/ani/' not in full_path:
            cmds.error(u"路径不对，必须包含 /ani/")
            return None

        if sys_name == 'Windows':

            # 拼凑路径
            pub_path = full_path.split('/ani/')[0].replace('W:', 'Z:') + '/ani/publish'
            print pub_path

        else:
            pub_path = full_path.split('/ani/')[0].replace('work', 'proj') + '/ani/publish'
            print pub_path


        # 2. 获取最新版本
        if os.path.exists(pub_path):
            versions = [x for x in os.listdir(pub_path) if '.v' in x and os.path.isdir(os.path.join(pub_path, x))]

            if versions:
                versions.sort()
                latest_folder = versions[-1]
                print u"找到最新文件夹:", latest_folder

                xml = os.path.join(pub_path, latest_folder, 'ani_assets.xml')
                laster_xml = xml.replace('\\', '/')
                return laster_xml  # 返回路径
            else:
                print u"没找到版本文件夹"
                return None
        else:
            print u"Publish 路径不存在"
            return None

    def get_namespaces_from_xml(self,xml_path):
        if not xml_path:
            return []  # 如果路径是空的，直接返回空列表

        # 1. 解析 XML 文件
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except Exception as e:
            print u"读取 XML 失败: %s" % e
            return []

        namespace_list = []

        # 2. 查找所有的 <asset> 标签并获取 namespace
        for asset_node in root.findall('asset'):
            ns = asset_node.get('namespace')
            if ns:
                namespace_list.append(ns)

        # 返回列表供后续使用
        return namespace_list

    def get_chr_ns(self):
        # 定义一个局部列表，比用全局变量更安全
        current_maya_list = []

        if cmds.objExists(grp_name):
            children = cmds.listRelatives(grp_name, children=True, fullPath=False) or []

            for child in children:
                if ':' in child:
                    ns = child.split(':')[0]
                    current_maya_list.append(ns)
                else:
                    print u'发现非引用物体: %s' % child
        else:
            print u'场景中没找到 %s 组' % grp_name

        # 【关键修改】必须把结果 return 出去
        return current_maya_list

    def get_change_report(self,xml_list, maya_list):
        # 1. 预处理
        diff_xml = sorted(list(set(xml_list) - set(maya_list)))
        diff_maya = sorted(list(set(maya_list) - set(xml_list)))

        # 结果容器
        deleted_items = []
        added_items = []
        changed_items = []

        # 提取所有涉及到的名字主干
        get_base = lambda x: x.rstrip('0123456789')
        all_bases = set([get_base(x) for x in diff_xml + diff_maya])

        # 2. 遍历归类
        for base in sorted(list(all_bases)):
            olds = [x for x in diff_xml if get_base(x) == base]
            news = [x for x in diff_maya if get_base(x) == base]

            match_count = min(len(olds), len(news))

            changed_items.extend(news[:match_count])
            added_items.extend(news[match_count:])
            deleted_items.extend(olds[match_count:])

        # 3. 打印结果
        print u"== == == == == == == == 对比报告 == == == == == == == == "
        print u"XML内物体数量: %s" % len(xml_list)
        print xml_list
        print u"Maya内物体数量: %s" % len(maya_list)
        print maya_list
        print u"----------------------------------------"
        print u"【被删除的】(XML有，Maya没了):", deleted_items
        print u"【纯新增的】(Maya新加的):", added_items
        print u"【发生改变】(版本升级):", changed_items
        return changed_items
        print u"=========================================="


    def run_check(self):
        target_xml_file = self.xml_path()
        list_from_xml = self.get_namespaces_from_xml(target_xml_file)

        # 2. 获取 Maya 里的列表
        list_from_maya = self.get_chr_ns()

        # 3. 只有当两个列表都成功拿到时（或者其中一个是空的也没关系），进行对比
        if list_from_xml is not None and list_from_maya is not None:
            change_list = self.get_change_report(list_from_xml, list_from_maya)
            if change_list:
                return u'这些资产 %s 对比上一版发生了命名空间的变化，请检查是否有修改' % change_list
            else:
                return ''
        else:
            print u"获取列表失败，无法进行对比。"
            return ''

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