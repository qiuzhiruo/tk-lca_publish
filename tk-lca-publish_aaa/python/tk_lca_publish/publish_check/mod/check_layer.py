#-*- coding=utf-8 -*-
import pymel.core as pm
import traceback

from proc.function_running_time import record_time

class StdCheck():
    def __init__(self,dialog):
        self.dialog = dialog
        self.check_name = u'检查是否含有layer'
        self.description = u'模型场景中不应该含有除defaultlayer之外制作人员自定义的display layer'
        self.auto_fix = True
        self.duty = u'艺术家本人'
        return

    @record_time(__file__)
    def run_check(self):
        try:
            layers_lst = pm.ls(type='displayLayer')
            if len(layers_lst)>1:
                return '场景中不能有任何layer，若有请制作人员手动删除，或点击自动修复'
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        l_layers = pm.ls(type='displayLayer')
        d_layers = {}
        for layer in l_layers:
            if layer.name() != 'defaultLayer':
                d_layers[layer.name()] = pm.editDisplayLayerMembers(layer, query=True, fullNames=True)
                try:
                    pm.editDisplayLayerMembers("defaultLayer", d_layers[layer.name()], noRecurse=True)
                    pm.delete(layer)
                except:
                    return 'Failed to clear layer:%s'%layer.name()
        return ''

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty
