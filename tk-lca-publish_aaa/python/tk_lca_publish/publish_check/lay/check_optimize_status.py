# -*- coding:utf-8 -*-

import traceback
import pymel.core as pm
import datetime as dt

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否优化过场景"
        self.description = u"optimize maya scene优化工具会在assets节点上留下时间记号，我们要确保publish之前场景执行过该工具。"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return


    def run_check(self):
        try:
            if pm.objExists('assets.optimize_scene_stamp'):
                now = dt.datetime.now()
                stamp_time = pm.Attribute('assets.optimize_scene_stamp').get()
                stamp_datetime = dt.datetime.strptime(stamp_time, '%Y-%m-%d %H:%M:%S')
                timedelta = now - stamp_datetime
                if timedelta.seconds//60 > 15 or timedelta.days != 0:
                    return u'最近一次场景优化检查不在15分钟内，请再次检查'
            else:
                return u'未执行optimize maya scene工具'

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Open the Tool'''
        import lay.optimize_maya_scene.ui.main as main
        #print main.__file__
        main.main()
        
        return ""


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


