# -*- coding: utf-8 -*-
# @Time    : 18-1-22 下午2:42
# @Author  : zhangzheng
__author__ = 'zhangzheng'
__maintainer__ = 'zhangzheng'


import os
import traceback
import json
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"动画穿插拍屏。"
        self.description = u"检测动画是否有对应版本的，角色穿插拍屏mov文件。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            if self.dialog.project['name'] == 'cat':
                return ""

            # Get assets
            import ani.lca_check_intersection.window as win
            try:
                all_assets_list = win.get_proj_assets(self.dialog.project['name'])
            except:
                all_assets_list = []
            d_assets = []
            if pm.objExists('|assets|chr'):
                for asset in pm.listRelatives('|assets|chr', c=True):
                    ns = ':'.join(asset.nodeName().split(':')[:-1])
                    isTrue = False
                    for asset_start in all_assets_list:
                        if ns.startswith(asset_start):
                            isTrue = True
                    if isTrue:
                        if pm.objExists(ns + ':body_geo') and pm.nodeType(ns + ':body_geo') == 'transform':
                            d_assets.append(asset)
            
            
            if len(d_assets) == 0:
                return ""
            else:
                notes = self.dialog.sg.find('Note', [['note_links', 'is', self.dialog.entity],
                                                     ['created_at', 'in_last', (1, 'DAY')]],
                                            ['content', 'user.HumanUser.login',
                                             'user.HumanUser.permission_rule_set'])

                for note in notes:
                    content = note['content']
                    if content is None:
                        continue
                    if isinstance(content, str):
                        content = content.decode('utf-8')
                    content = content.lower().replace(' ', '').replace('-', '')
                    if any(i in content for i in (u'跳过动画穿插检查',
                                                  u'skipaniintersection' )) \
                            and note['user.HumanUser.permission_rule_set'] \
                            and note['user.HumanUser.permission_rule_set']['name'] in ['Lead', 'Admin', 'Manager']:
                        print 'Found a note that allows skipping this check.'
                        return ""

                file_path = pm.sceneName()
                ani_intersection_path = os.path.join(os.path.dirname(file_path), 'ani_intersection')
                if not os.path.isdir(ani_intersection_path):
                    # print ani_intersection_path
                    return u"没有发现动画穿插拍屏文件夹，请提交动画穿插拍屏并检查 %s。" % ani_intersection_path
                version_name = os.path.splitext(os.path.basename(file_path))[0]
                version_id = version_name.split('.')[-1]
                version_num = int(version_id[1:])
                all_ani_intersection_dir = []
                for ver in range(version_num,version_num-3,-1):
                    new_ver = 'v%03d' % ver
                    version_dir_naem = version_name.replace(version_id,new_ver)
                    ani_intersection_ver = os.path.join(ani_intersection_path, version_dir_naem)
                    if os.path.isdir(ani_intersection_ver):
                        # print ani_intersection_ver
                        all_ani_intersection_dir.append(ani_intersection_ver)
                if len(all_ani_intersection_dir) == 0:
                    return u"没有发现三个版本内的动画穿插拍屏文件夹，请提交动画穿插拍屏并检查 %s。" % version_name
                
                mov_true = None
                for ani_intersection_ver in all_ani_intersection_dir:
                    ani_intersection_mov = list()
                    try:
                        ani_intersection_mov = [i.split('.')[1] for i in os.listdir(ani_intersection_ver) if i.endswith('.mov')]
                    except:
                        ani_intersection_mov = []
                    if len(ani_intersection_mov) == 0 :
                        mov_true = 0

                    err_intersections = [mov for mov in d_assets if mov not in ani_intersection_mov]
                    if len(err_intersections) != 0:
                        mov_true = 1
   
                    mov_true = 'ok'
                
                
                if mov_true == 'ok':
                    return ""
                elif mov_true == 0:
                    return u"发现没有动画穿插检查拍屏的角色，请提交动画穿插拍屏并检查 "
                elif mov_true == 1:
                    return u"发现动画穿插检查拍屏的角色数量与文件角色数量等，请提交动画穿插拍屏并检查 "

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
