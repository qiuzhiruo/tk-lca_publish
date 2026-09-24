# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.01
#
# Description: 
#
############################################

import traceback
import pprint
import os


# All system check classes will use StdCheck as the class name.
class StdCheck():
	def __init__(self, dialog):
		self.dialog = dialog
		self.check_name = u"检查版本的标签是否选择。"
		self.description = u"检查版本的标签是否选择,已有精模不能再提交粗模"
		self.auto_fix = False
		self.duty = u"艺术家本人。"
		return

	def run_check(self):

		try:
			self.dialog.version_tag = self.dialog.w_sys.comboBox_tag.currentText()

			if self.dialog.version_tag == '':
				return u"还没有选择版本的标签。"

			if self.dialog.version_tag == u"粗模":
				sg_version_list = self.dialog.sg.find('Version', [['sg_task.Task.id', 'is', self.dialog.task['id']]],
				                                      ['tag_list','sg_version_type'])

				has_jm = False
				for version in sg_version_list:

					if version['sg_version_type']=='Downstream':
						tag_list = version['tag_list']
						for tag in tag_list:

							#self.dialog.print_log('tag:' + tag)
							if tag == "精模":
								has_jm = True
								break
				if has_jm==True:
					return u"之前的版本已经有精模的标签所以不能提交粗模。。"

					# last_version=self.dialog.sg.find_one('Version', [['id', 'is', self.dialog.task['id']]], ['sg_status_list'])

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
