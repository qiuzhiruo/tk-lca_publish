# -*- coding:utf-8 -*-
import maya.cmds as cmds
import pymel.core as pm
import traceback


# check if assets were hidden

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查是否隐藏资产'
        self.description = u'使用的资产不可以隐藏 -- keran'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:
            seq_start_frame = cmds.playbackOptions(q=True, min=True) # 1001
            seq_end_frame = cmds.playbackOptions(q=True, max=True) # 1020

            hidden_assets = []
            hidden_assets_key = []
            checklist = cmds.listRelatives('|assets', f=True)
            for cl in checklist:
                if cl == '|assets|lay':
                    continue
                inner = cmds.listRelatives(cl, f=True)
                if not inner:
                    continue
                for i in inner:
                    keys = cmds.keyframe(i+".visibility", q=1)
                    # 如果 master 有 多个key 帧
                    if keys and len(keys)>1:
                        # 获取镜头时长范围内的 key 帧列表
                        keys_frames = [ii for ii in keys if ii >= seq_start_frame and ii <= seq_end_frame] # [1006.0, 1013.0]
                        #如果镜头时长范围内有 key 帧，则看key帧情况，是否有key了隐藏
                        if keys_frames!=[]:
                            vis_values = []
                            for key_frame in keys_frames:
                                print key_frame,type(key_frame),cmds.getAttr(i + '.visibility',t=key_frame)
                                vis_values.append(cmds.getAttr(i + '.visibility',t=key_frame))
                            # print vis_values
                            # 看看 是不是 全是 隐藏情况
                            if True not in vis_values:
                                hidden_assets_key.append(i)
                        #如果镜头时长范围内无 key 帧，则直接获取镜头起始帧的值，看是否为隐藏
                        else:
                            vis_value = cmds.getAttr(i + '.visibility',t=seq_start_frame)
                            if not vis_value:
                                hidden_assets_key.append(i)
                        # vis_values = []
                        # for k in keys:
                        #     vis_values.append(cmds.getAttr(i + '.visibility',t=k))
                        #     if len(vis_values)>1 and len(list(set(vis_values)))==1:
                        #         if not list(set(vis_values))[0]:
                        #             hidden_assets_key.append(i)
                        #             break
                        
                    # 如果 master 有 一个key 帧
                    elif keys and len(keys) ==1:
                        if not cmds.getAttr(i + '.visibility'):
                            hidden_assets_key.append(i)
                    # 如果 master 没有 key 帧
                    else:
                        if not cmds.getAttr(i + '.visibility'):
                            # name = i.longName()
                            hidden_assets.append(i)
            returnStr = ''
            if hidden_assets:
                returnStr = u"以下资产是隐藏的:\n" + '\n'.join(hidden_assets)+u'如果不需要请remove'+'\n'
            if hidden_assets_key:
                returnStr += u'以下资产k了隐藏 在 帧范围内 一直是隐藏状态:\n' + '\n'.join(hidden_assets_key)+u'\n如果不需要请remove'
            if returnStr:
                return returnStr
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
