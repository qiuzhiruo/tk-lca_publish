# -*- coding:utf-8 -*-

import traceback
import os
import sys
import pymel.core as pm
import maya.cmds as cmds

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否使用了公共环境以外的plug-in"
        self.description = u"检查是否使用了公共环境以外的plug-in"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self): 
        try:
            other_avaliable_plugins=['Mayatomr','MASH',"poseInterpolator"]
            maya_version = cmds.about(v=True)
            maya_plugin_path = os.getenv('MAYA_LOCATION')+'/bin/plug-ins/'

            lca_app_path = os.getenv('LC_APP_PATH')
            toolset = os.getenv('LC_TOOLSET')
            # if sys.platform.startswith("win"):
            #     lca_plugin_path = 'U:/toolset/applications/maya/'+maya_version+'-x64/plugins'
            #     lca_python_plugin_path = 'U:/toolset/applications/maya/plugins/'
            # elif sys.platform.startswith("linux"):
            #     lca_plugin_path = '/mnt/utility/toolset/applications/maya/'+maya_version+'-x64/plugins'
            #     lca_python_plugin_path = '/mnt/utility/toolset/applications/maya/plugins/'

            lca_plugin_path = '%s/maya/%s-x64/plugins' % (lca_app_path,maya_version)
            lca_python_plugin_path = '%s/maya/plugins/' % lca_app_path

            maya_plugins = []
            if os.path.exists(maya_plugin_path):
                files = os.listdir(maya_plugin_path)
                for f in files:
                    #f=files[0]
                    if '.mll' in f or '.py' in f or '.so' in f:
                        maya_plugins.append(f.replace('.mll',''))
            
            lca_plugins = []
            if os.path.exists(lca_plugin_path):
                files = os.listdir(lca_plugin_path)
                for f in files:
                    #f=files[0]
                    if '.mll' in f or '.py' in f or '.so' in f:
                        lca_plugins.append(f.replace('.mll',''))


            lca_python_plugins = [] 
            if os.path.exists(lca_python_plugin_path):
                files = os.listdir(lca_python_plugin_path)
                for f in files:
                    #f=files[0]
                    if '.mll' in f or '.py' in f or '.so' in f:
                        lca_python_plugins.append(f.replace('.mll',''))

            avaliable_plugins = maya_plugins + lca_plugins +other_avaliable_plugins+lca_python_plugins
            

            rs=u""
            using_plugins_message = cmds.pluginInfo(q=1,pluginsInUse=1)
            if using_plugins_message == None:
                return rs

            using_plugins = []
            i=0
            for m in using_plugins_message:
                if i%2==0:
                    using_plugins.append(m)
                i=i+1
                
        
            
            print using_plugins
            for plugin in using_plugins:
                #plugin = using_plugins[2]
                if not plugin in avaliable_plugins:
                    rs=rs+plugin+u"  is not a avaliable plugin in LCA\n"
            print rs
            return rs

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty