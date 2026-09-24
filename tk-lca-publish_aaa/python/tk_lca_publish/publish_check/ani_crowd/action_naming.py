# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.10
#
# Description: As the description shows below
#
############################################

import os
import traceback


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"行为数据命名规范。"
        self.description = u"行为数据命名规范。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            invalid_names = []
            for data in self.dialog.actions_data:
                name = data['name']
                valid = self.CheckStringIsValid(name)
                if not valid:
                    invalid_names.append(name)

            if invalid_names:
                return u'以下行为数据命名不符合规范：\n'+'\n'.join(invalid_names)

            return ''
        except:
            return traceback.format_exc()

    def CheckStringIsValid(self, inString):
        isValid = True;
        if len(inString) >0:
            if inString[0].isalpha() == False:
                isValid = False
                return isValid;
            for i in range(len(inString)):
                if inString[i].isdigit() == False:
                    if inString[i].isalpha() == False:
                        if inString[i] != "_":        
                            isValid = False
                            return isValid;
            return isValid;
        else:
            isValid = False
            return isValid;

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
