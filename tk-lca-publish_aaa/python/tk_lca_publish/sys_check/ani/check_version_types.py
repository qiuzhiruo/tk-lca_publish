# -*- coding:utf-8 -*-
__author__ = 'makong'

import os
import sys
import traceback

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查当前要Pa的版本是否合理"
        self.description = u"test 模式下可以pa任何版本，其它模式下:\npa downstream 版本前，必须有checked版本；\n上一版若是Downstream版，且无帧范围修改，只可趴Downstream版\nz1 和 z33 场次可以直接趴Downstream版\n"
        self.auto_fix = False
        self.duty = u"流程管理"
        return

    def run_check(self):
        try:
            #Entity: {'type': 'Shot', 'name': 'm60550', 'id': 10884}
            if self.dialog.project['name'].lower() == 'tpr':
                return ""

            if self.dialog.entity['type'] == 'Shot' and self.dialog.w_sys.comboBox_tag.currentText()!=u'测试':
                vers = self.dialog.sg.find('Version', [['project', 'is', self.dialog.project],
                                                       ['entity', 'is', self.dialog.entity],
                                                       ['sg_task', 'name_is', 'animation']], ['sg_version_type', 'tags'])
                print vers
                if self.dialog.publish_mode != 2:
                    if vers and vers[-1]['sg_version_type'] == 'Downstream' and u'测试' not in [i['name'].decode('utf-8') for i in vers[-1]['tags']]:
                        shot_info = self.dialog.sg.find('Shot', [['project', 'is', self.dialog.project],
                                                                 ['code', 'is', self.dialog.entity['name']]],
                                                        ['sg_ani_cut_in', 'sg_ani_cut_out'])[0]
                        if not shot_info['sg_ani_cut_in'] or not shot_info['sg_ani_cut_out']:
                            return u'该镜头上一版为Downstream版,且未发现有Ani Cut In/Out数值,只可趴Downstream版!'
                
                if self.dialog.publish_mode == 2:
                    # z11 场次默认可以直接趴ds
                    if self.dialog.step['name'] == 'ani' and (self.dialog.entity['name'].startswith('z1') or self.dialog.entity['name'].startswith('z33')):
                        return ""
                    else:
                        if vers:
                            l_types = [v['sg_version_type'] for v in vers ]
                            #print l_types
                            if 'Checked' in l_types:
                                aniTask = self.dialog.sg.find('Task', [['entity', 'is', self.dialog.entity],
                                                       ['step','is',{'type': 'Step', 'id': 5, 'name': 'ani'}],
                                                       ['content','is','animation']], ['content','step','sg_status_list'])
                                aniTask_status = aniTask[0]['sg_status_list']
                                print aniTask_status
                                # 任务状态 为 rtk 可以 pa check/ds，如果不是 rtk，不能 pa ds，防止 此时还在剪辑审核，pa 到下游后，后续有修改还需要再返回
                                # 此情况需要等剪辑审核完毕，无需修改，由制片去 vp 升级版本。如果需要修改，制作继续 pa check
                                if aniTask_status == 'rtk':
                                    return ""
                                else:
                                    if l_types[-1] == 'Downstream':
                                        return ""
                                    else:
                                        return u'当前任务状态不是 rtk，且上个(最新)版本不是 Downstream 版本，不可 趴 Downstream 版本，请确认'
                            else:
                                return u'该镜头还没有checked版本，请确认'
                        else:
                            return u'该镜头还没有checked版本，请确认'
            
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return ""

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
