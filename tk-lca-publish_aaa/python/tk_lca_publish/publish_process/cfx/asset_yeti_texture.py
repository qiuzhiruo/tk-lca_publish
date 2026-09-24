# coding: utf-8

__author__ = 'john'
import os
import shutil
import traceback
import glob
import pymel.core as pm

# All publish process will use StdProcess as the class name.

class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝 Yeti贴图"
        self.description = u"将 Yeti 用到的 texture 复制到publish文件夹并修改相应 texture 节点的路径参数."

    def proceed(self):
        try:
            yeti_node_list=pm.ls(typ='pgYetiMaya')
            if yeti_node_list:
                # copy tex to publish
                tex_dir = self.dialog.version_dir+'/yeti_texture/'
                if os.path.isdir(tex_dir):
                    shutil.rmtree(tex_dir)
                os.makedirs(tex_dir)

            for yeti_node in yeti_node_list:
                for tex_node in pm.pgYetiGraph(yeti_node, listNodes=1, type='texture'):
                    tex = pm.pgYetiGraph(yeti_node, node=tex_node, param='file_name', getParamValue=True)
                    if '<UDIM>' in tex:
                        l_tex_src = glob.glob(tex.replace('<UDIM>', '*'))
                    else:
                        l_tex_src = [tex]

                    for tex_src in l_tex_src:
                        if os.path.isfile(tex_src):
                            shutil.copyfile(tex_src, tex_dir+os.path.basename(tex_src))
                            print '  Copy file:' + tex_src
                        else:
                            print '  Not exist:' + tex_src

                    pm.pgYetiGraph(yeti_node, node=tex_node, param="file_name", setParamValueString=(tex_dir + tex.split('/')[-1]))

                # set the image search path
                yeti_node.imageSearchPath.set(tex_dir)


            return ''
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
