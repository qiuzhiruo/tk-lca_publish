# -*- coding:utf-8 -*-
import pymel.core as pm
from proc.function_running_time import record_time


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"角色非寻常比例，请手动检查角色turntable。"
        self.description = u"当角色高度小于1.4米时，自动生成的turntable可能比例不合适，需要模型师手动检查。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        if self.dialog.d_assets_info[self.dialog.entity['name']]['type'] != 'chr':
            return ''

        skin_grp_res = pm.listRelatives("|master|poly|hi|mesh_grp|skin_grp", c=True, ad=True)
        body_geo = next((res for res in skin_grp_res if res.nodeName() == 'body_geo'), None)

        if not body_geo:
            return u'没有body_geo，无法检查turntable是否合适，请检查body_geo是否命名错误'

        bbx = body_geo.boundingBox()
        height = bbx[1][1]
        if height <= 14:
            msg = u'当角色高度小于1.4米时，自动生成的角色头部turntable可能比例不合适，需要模型师手动打开turntable检查.打开turntable看看比例合不合适，不合适进行调整\n' \
                  u'                                           如果已经检查请点击 Yes'
            result = pm.confirmDialog(title=u"注意！！！" , message=msg, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            if result == 'No':
                return u'当角色高度小于1.4米时，需手动打开turntable检查。'
        return ''

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
