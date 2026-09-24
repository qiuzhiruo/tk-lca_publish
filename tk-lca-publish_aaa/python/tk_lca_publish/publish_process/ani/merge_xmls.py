# -*- coding:utf-8 -*-
import os,sys,json,re
import platform
import traceback
import shutil
import codecs
# import maya.cmds as cmds
# sys.path.append('/mnt/work/shome/yangshuai/push_git/lib')
import production.pipeline.lcProdProj as lcpp
# if sys.platform.startswith('linux'):
try:
    from lxml import etree as ET
except:
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

from production import shotgun_connection
from production.translate_os_path import osPathConvert
sg = shotgun_connection.Connection('get_shot_info').get_sg()

'''
这个脚本用来在大场面场景拆分成几个镜头之后publish的时候合并xml到主镜头里
2025.07.21update:现在对于二次拆分的镜头，由于为了审核和rtk方便，进行二次拆分的一次拆分镜头不再出缓存xml，只作合并拍屏用
现在标注类似“z99640大场面拆分镜头_提交_part01，z99700拆分镜头”含有“提交“字段外加“{镜头号}大场面拆分镜头“才会认定为拆分镜头
'''


# 这个是用一般库手动实现parser = ET.XMLParser(remove_blank_text=True)的方法
def strip_whitespace(elem):
    # 清除自身 text/tail 中仅含空白的部分
    if elem.text  and not elem.text.strip():
        elem.text = None
    if elem.tail and not elem.tail.strip():
        elem.tail = None
    for child in elem:
        strip_whitespace(child)

def recursive_merge_inst_nodes(main_root,minor_root,main_asset_list=[],main_group_list=[]):
    tmp_main_asset_list=[]
    tmp_main_group_list={}
    for c in main_root.getchildren():
        if c.tag == 'instanceList':
            # print(c.tag)
            for m in minor_root.getchildren():
                if m.tag == 'instanceList':
                    recursive_merge_inst_nodes(c, m)
            # continue
            # for cc in c.getchildren():
            #     if cc.tag == 'instance' and 'type' in cc.attrib and 'name' in cc.attrib:
            #         if cc.attrib['type']=='reference':
            #             main_group_list.append(cc.attrib['name'])
            #         else if cc.attrib['type'] == 'reference':
            #             main_asset_list.append(cc.attrib['name'])
            #         else if cc.attrib['type'] == 'instanceList':


        if c.tag == 'instance': #skip
            if 'type' in c.attrib and 'name' in c.attrib:
                if c.attrib['type']=='group':
                    tmp_main_group_list[c.attrib['name']]=c
                elif c.attrib['type'] == 'reference':
                    tmp_main_asset_list.append(c.attrib['name'])
                    main_asset_list.append(c.attrib['name'])#Do we need this?
    if tmp_main_asset_list or tmp_main_group_list:
        for m in minor_root.getchildren():
            if m.tag == 'instance':
                if  'type' in m.attrib and 'name' in m.attrib:
                    if m.attrib['type']=='reference':
                        if m.attrib['name'] not in tmp_main_asset_list:
                            print('----')
                            print('Merge xml,add asset: ')+m.attrib['name']
                            print('----')
                            # ET.SubElement(main_root, m.tag, m.attrib)#append(m)?
                            main_root.append(m)
                        else:
                            try:
                                for instance_child in m.getchildren():
                                    if instance_child.tag=='arbitraryList':
                                        for attr in instance_child.getchildren():
                                            if 'name' in attr.attrib:
                                                if attr.attrib['name'] == 'viewable':
                                                    print('WARNING:Might be a mistake, get two repeat assets in shot xml:')
                                                    print(m.attrib['name'])
                                                    break
                            except:
                                pass
                    elif m.attrib['type']=='group':
                        if m.attrib['name'] not in tmp_main_group_list.keys():
                            main_root.append(m)
                        else:
                            recursive_merge_inst_nodes(tmp_main_group_list[m.attrib['name']], m)


    return main_root
            

def merge_shot_xmls(main_xml,
                minor_xml,
                output_new_xml
                ):
    parser=None
    main_tree=None
    minor_tree=None
    manually_remove_blank=False

    if main_xml and minor_xml and output_new_xml:
        if not os.path.isfile(main_xml) or not os.path.isfile(minor_xml):
            print('Xml path for either main_xml or minor_xml does NOT EXIST!Please check.')
        else:
            try:
                parser = ET.XMLParser(remove_blank_text=True)
            except:
                # 手动处理manually_remove_blank
                print('='*30)
                print('manually_remove_blank for this xml')
                print('='*30)
                manually_remove_blank = True

            main_tree = ET.parse(main_xml,parser)
            minor_tree = ET.parse(minor_xml,parser)

            main_root = main_tree.getroot()
            minor_root = minor_tree.getroot()

            if manually_remove_blank:
                strip_whitespace(main_root)
                strip_whitespace(minor_root)

            # main_inst_nodes = main_root.xpath('//instance')
            #Do not do it in cursive part to make it more flexible,can delete prp for example.
            type_list = ['env','chr','asb','flg','scn','prp','rra']
            main_instanceList_root = None
            minor_instanceList_root = None
            #root -> instanceList -> <instance name="assets" type="group"> -> instanceList(get this and loop it)
            for c in main_root.getchildren()[0].getchildren():#...
                if c.attrib['name']=='assets':
                    for cc in c.getchildren():
                        if cc.tag == 'instanceList':
                            main_instanceList_root=cc
                            break
            for c in minor_root.getchildren()[0].getchildren():#...
                if c.attrib['name']=='assets':
                    for cc in c.getchildren():
                        if cc.tag == 'instanceList':
                            minor_instanceList_root=cc
                            break

            #loop instancelist, merge prp,scn,chr...etc.If lack this type of assets, merge whole group.
            if main_instanceList_root is not None and minor_instanceList_root is not None:
                for i in minor_instanceList_root.getchildren():
                    for scenegraph_layer in type_list:
                        if i.attrib['name']==scenegraph_layer:
                            have_this_scenegraph_layer=False
                            for ii in main_instanceList_root.getchildren():
                                if ii.attrib['name']==scenegraph_layer:
                                    have_this_scenegraph_layer = True
                                    recursive_merge_inst_nodes(ii,i)#self.recursive_merge_inst_nodes(ii,i)
                                    # print(ii.attrib)
                            if not have_this_scenegraph_layer:
                                main_instanceList_root.append(i)
            else:
                print('ERROR:NO instanceList_root FOUND!')
    try:
        main_tree.write(output_new_xml, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    except:
        main_tree.write(output_new_xml, xml_declaration=True, encoding='UTF-8')
        #使用标准库实现lxml pretty_print
        # 将 ElementTree 转为字符串
        xml_str = ET.tostring(main_root, encoding='utf-8')

        # 使用 minidom 进行 pretty-print
        parsed = minidom.parseString(xml_str)
        pretty_xml = parsed.toprettyxml(indent="  ")

        # 写入文件（去除多余空行）
        with codecs.open(output_new_xml, 'w', encoding='utf-8') as f:
            f.write('\n'.join([line for line in pretty_xml.split('\n') if line.strip()]))

def merge_aniasset_xmls(main_xml,
                minor_xml,
                output_new_xml
                ):
    parser=None
    main_tree=None
    minor_tree=None
    manually_remove_blank=False

    if main_xml and minor_xml and output_new_xml:
        if not os.path.isfile(main_xml) or not os.path.isfile(minor_xml):
            print('Xml path for either main_xml or minor_xml does NOT EXIST!Please check.')
        else:
            try:
                parser = ET.XMLParser(remove_blank_text=True)
            except:
                #paser not available in xml,only use in lxml
                manually_remove_blank = True

            main_tree = ET.parse(main_xml,parser)
            minor_tree = ET.parse(minor_xml,parser)

            main_root = main_tree.getroot()
            minor_root = minor_tree.getroot()

            if manually_remove_blank:
                strip_whitespace(main_root)
                strip_whitespace(minor_root)

            main_ani_assets_list=[]#store assets we have

            try:
                main_inst_nodes = main_root.xpath('//anim')[0].getchildren()
                minor_inst_nodes = minor_root.xpath('//anim')[0].getchildren()
            except:
                main_inst_nodes = main_root.findall('.//asset')
                minor_inst_nodes = minor_root.findall('.//asset')
            #loop all 'asset' under 'anim' tag
            for asset in main_inst_nodes:
                if asset.tag == 'asset':
                    main_ani_assets_list.append(asset.attrib['namespace'])

            for asset in minor_inst_nodes:
                if asset.tag == 'asset':
                    if asset.attrib['namespace'] not in main_ani_assets_list:
                        main_ani_assets_list.append(asset.attrib['namespace'])
                        main_root.append(asset)
                    else:
                        print('-'*60)
                        print('WARNING:Might be a mistake, get two repeat assets in aniasset xml:')
                        print(asset.attrib['namespace'])
                        print('-'*60)

    try:
        main_tree.write(output_new_xml, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    except:
        # print(type(main_tree))
        # print(ET.tostring(main_root, pretty_print=True).decode())
        print('='*30)
        print('manually pretty_print this xml')
        print('='*30)
        main_tree.write(output_new_xml, xml_declaration=True, encoding='UTF-8')
        #使用标准库实现lxml pretty_print
        # 将 ElementTree 转为字符串
        xml_str = ET.tostring(main_root, encoding='utf-8')

        # 使用 minidom 进行 pretty-print
        parsed = minidom.parseString(xml_str)
        pretty_xml = parsed.toprettyxml(indent="  ")

        # 写入文件（去除多余空行）
        with codecs.open(output_new_xml, 'w', encoding='utf-8') as f:
            f.write('\n'.join([line for line in pretty_xml.split('\n') if line.strip()]))

# @classmethod
# 1.获取当前镜头的proj, seq, shot
def get_current_shot_info():
    ctx = sgtk.platform.current_engine().context
    proj = ctx.project['name'].lower()
    shot = ctx.entity['name']
    seq = shot[:-3]

    return proj, seq, shot

# 3.获取当前镜头的拆分镜头
#返回：所有拆分镜头，是否是拆分流程的主镜头（进行拆分的镜头），是否是分镜头（因为有可能又是主镜头又是分镜头），主镜头镜头号
def get_all_split_shot(proj, shot):
    split_mainshot_or_not = False
    split_minorshot_or_not = False
    all_split_shot_info = {}
    main_shot = None

    if any(x is None or x == "" for x in (proj, shot)):
        proj, seq, shot = get_current_shot_info()

    print('Current shot for merge/split is:')
    print(shot)

    #获取当前镜头的描述
    current_shot_sg_info = sg.find_one("Shot", [["project.Project.name", "is", proj], ["code", "is", shot]],
                                    ["sg_sequence", "description", "code"])
    current_shot_description = current_shot_sg_info["description"]
    current_shot_description_str = json.dumps(current_shot_description, ensure_ascii=False, indent=4).decode('utf-8')

    #判断是否有这个镜头的拆分镜头
    #2025.07.21update:现在对于二次拆分的镜头，由于为了审核和rtk方便，进行二次拆分的一次拆分镜头不再出缓存xml，只作合并拍屏用
    #现在标注类似“z99640大场面拆分镜头_提交_part01，z99700拆分镜头”含有“提交“字段外加“{镜头号}大场面拆分镜头“才会认定为拆分镜头
    split_shot_filters = [
        ["project.Project.name", "is", proj],
        ['sg_status_list', 'is_not', 'omt'],
        ["sg_sequence", "is", current_shot_sg_info["sg_sequence"]],
        ["description", "contains", u"{0}大场面拆分镜头".format(shot)],
        ["description", "contains", u"提交"]
    ]
    split_all_shots = sg.find("Shot", split_shot_filters, ["description", "code"])

    #分镜头标注有"大场面拆分镜头",且又进行了拆分，先加入拆分镜头的拆分镜头;然后寻找该主镜头的其它拆分镜头，也加入分镜头统计
    #主镜头描述里没有"大场面拆分镜头"字段
    if u"大场面拆分镜头" in current_shot_description_str: #是否允许拆中拆？
        #寻找其它的拆分镜头，也加入分镜头统计
        all_split_shot_info.setdefault(
            current_shot_sg_info["code"], current_shot_description)
        file_name_filter = u'([a-z][0-9]{5})大场面拆分镜头'
        #查找这个分镜头的主镜头
        match = re.search(file_name_filter, current_shot_description_str)
        if match:
            main_shot = match.group(1)
        else:
            print('ERROR: Cannot find main_shot!')
            print(file_name_filter,current_shot_description_str)
            # return '','','',''
            return None,None,None,None

        #**允许拆中拆，但是这里不再递归重新合并生成分镜头的xml了（也就是不考虑分镜头的分镜头再往下拆分出的分镜头了），暂时应该没有这种情况**
        for sas in split_all_shots:
            all_split_shot_info.setdefault(sas["code"], sas['description'])
        #寻找其它的拆分镜头，也加入分镜头统计
        split_shot_filters = [
            ["project.Project.name", "is", proj],
            ['sg_status_list', 'is_not', 'omt'],
            ["sg_sequence", "is", current_shot_sg_info["sg_sequence"]],
            ["description", "contains", u"{0}大场面拆分镜头".format(main_shot)],
            ["description", "contains", u"提交"]
        ]
        split_all_shots = sg.find("Shot", split_shot_filters, ["description", "code"])
        for sas in split_all_shots:
            all_split_shot_info.setdefault(sas["code"], sas['description'])

        split_minorshot_or_not = True
        return all_split_shot_info, split_mainshot_or_not, split_minorshot_or_not, main_shot

    #非拆分。不是分镜头，且不是主镜头
    if not split_all_shots:
        print('It is not a split shot')
        # pm.confirmDialog(title="Warning", message=u"未检测到该镜头在Shotgun上对应的大场面拆分镜头,请反馈TD或制片!")
        # return '','','',''
        return None,None,None,None

    #那么此镜头是主镜头了
    main_shot = shot
    for sas in split_all_shots:
        #split_all_shots里的是拆分镜头了，加入分镜头统计
        all_split_shot_info.setdefault(sas["code"], sas['description'])
    
    split_mainshot_or_not = True

    return all_split_shot_info, split_mainshot_or_not, split_minorshot_or_not, main_shot



class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"大场景拆分新流程，合并主次镜头xml到一起，存在主镜头中"
        self.description = u"Merge minor shot's xml to major shot's xml"
        return

    def proceed(self):
        try:
            proj = self.dialog.project['name'].lower()
            dept = self.dialog.step['name']
            shot = self.dialog.entity.get('name')
            # proj = 'sgl'
            # shot = 'z99999'
            # dept = 'ani'

            all_split_shot_info, split_mainshot_or_not, split_minorshot_or_not, main_shot = get_all_split_shot(proj, shot)
            #不是拆分镜头。或出现了异常报错，跳过
            if any(x is None or x == '' for x in (all_split_shot_info, split_mainshot_or_not, split_minorshot_or_not, main_shot)):
                return ''
            #如果publish的是拆分镜头的主镜头（新流程），我们需要脚本合并所有的xml
            projInfo = lcpp.lcProdProj()
            projInfo.setProj(proj)
            print('Test if need merge massive asset shot\'s xml')
            # ani_xml = projInfo.lcGetLayXml(shot,copy=False,clear_assets=False)[0]
            if (split_mainshot_or_not == True or split_minorshot_or_not == True) and all_split_shot_info is not None and main_shot is not None:
                ani_xml = projInfo.get_lay_xml(main_shot, dept, copy=False,clear_assets=False)
                if not ani_xml and dept=='flo':
                    ani_xml = projInfo.get_lay_xml(main_shot, 'ani', copy=False,clear_assets=False)
                    if ani_xml:
                        ani_xml=ani_xml[0]
                else:
                    ani_xml=ani_xml[0]
                if not ani_xml:
                    print('***Error: No shot xml found in main shot!!***')
                    return ''
                ani_assets_xml = os.path.dirname( os.path.dirname(ani_xml) )+'/ani_assets.xml'
                if not ani_assets_xml:
                    print('***Error: No ani_asset xml found in main shot!!***')
                    return ''
                i = 1
                backup_shot_xml = ani_xml.split('/scene_graph_xml/')[0]+'/scene_graph_xml/copy'+str(i)+'_'+ani_xml.split('/')[-1]
                origin_major_xml = ani_xml.split('/scene_graph_xml/')[0]+'/scene_graph_xml/origin'+'_'+ani_xml.split('/')[-1]
                backup_ani_assets_xml = ani_assets_xml.split('ani_assets.xml')[0]+'copy'+str(i)+'_'+ani_assets_xml.split('/')[-1]
                origin_ani_assets_xml = ani_assets_xml.split('ani_assets.xml')[0]+'origin'+'_'+ani_assets_xml.split('/')[-1]
                #如果有origin_major_xml的话，说明当前xml是已经合并过分镜头的版本了，需要用原始文件更新
                #即首次合成xml的时候我们一定要使用最原始的文件。因为当前的文件已经是合成之后覆盖了原始文件的xml，如果新更新的删掉了某个资产，直接合是删不掉的。因此先获取origin_xml
                #copyfile() 只复制文件内容，不会复制权限；使用 shutil.copy() 可能更稳定
                if os.path.isfile(origin_major_xml):
                    shutil.copy(origin_major_xml, ani_xml)
                if os.path.isfile(origin_ani_assets_xml):
                    shutil.copy(origin_ani_assets_xml, ani_assets_xml)
                while os.path.isfile(backup_shot_xml):
                    i+=1
                    backup_shot_xml = ani_xml.split('/scene_graph_xml/')[0]+'/scene_graph_xml/copy'+str(i)+'_'+ani_xml.split('/')[-1]
                    backup_ani_assets_xml = ani_assets_xml.split('ani_assets.xml')[0]+'copy'+str(i)+'_'+ani_assets_xml.split('/')[-1]
                print('origin_xml:')
                print(ani_xml)
                print(ani_assets_xml)
                #备份原有的xml,防止意外，之后新xml会覆盖掉这个
                shutil.copy(ani_xml, backup_shot_xml)
                shutil.copy(ani_assets_xml, backup_ani_assets_xml)
                #pu主镜头的话备份原始文件；pu分镜头的话主镜头已经Pu过了，一定有备份了。
                if split_mainshot_or_not:
                    shutil.copy(ani_xml, origin_major_xml)
                    shutil.copy(ani_assets_xml, origin_ani_assets_xml)
                print('backup success!')
                print(backup_shot_xml)
                print(backup_ani_assets_xml)
                #获取所有的拆分镜头,开始合并xml.
                
                for shot in all_split_shot_info:
                    latest_mainshot_xml = projInfo.get_lay_xml(shot, dept, copy=False,clear_assets=False)
                    if not latest_mainshot_xml and dept == 'flo':
                        latest_mainshot_xml = projInfo.get_lay_xml(shot, 'ani', copy=False,clear_assets=False)
                        if not latest_mainshot_xml:
                            print('No xml found in'+ shot+', this shot might have not started yet.Skip.')
                            continue
                    if latest_mainshot_xml is not None:
                        minor_ani_assets_xml = os.path.abspath(os.path.join(latest_mainshot_xml[0], "..", ".."))+'/ani_assets.xml'
                        if not os.path.isfile(minor_ani_assets_xml):
                            print('No ani asset xml found')
                            continue
                        print('---')
                        print('merge: '+shot)
                        print('use this mainshot xml: ' + latest_mainshot_xml[0])
                        print('use this minor_ani_assets_xml xml: ' + minor_ani_assets_xml)
                        print('---')
                        merge_shot_xmls(ani_xml,latest_mainshot_xml[0],ani_xml)
                        merge_aniasset_xmls(ani_assets_xml,minor_ani_assets_xml,ani_assets_xml)
            # return "Merge big xml done."
            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

# if __name__ == '__main__':
#     test = StdProcess('test')
#     test.proceed()
#     print('success!')
#     output_xml='/mnt/proj/projects/sgl/shot/d90/d90680/flo/publish/d90680.flo.final_layout.v001/scene_graph_xml/test.xml'
#     main_xml='/mnt/proj/projects/sgl/shot/d90/d90680/flo/publish/d90680.flo.final_layout.v001/scene_graph_xml/d90680.xml'
#     minor_xml='/mnt/proj/projects/sgl/shot/d90/d90685/flo/publish/d90685.flo.final_layout.v001/scene_graph_xml/d90685.xml'
#     # merge_shot_xmls(main_xml,minor_xml,output_xml)
#     merge_shot_xmls(main_xml,minor_xml,output_xml)