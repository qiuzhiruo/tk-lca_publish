# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Xiang Quan
#
# Date: 2015.07
#
# Description: 1. Check all transform names under the hierarchy |master|poly|hi|[grp]
#              2. Fix bad node names automatically
#
############################################

import traceback
import os
import re
import pymel.core as pm

from sgtk.platform.qt import QtGui
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck(object):
    FRONT_KEYWORDS = ['L','R']
    END_KEYWORDS = ['PLY', 'SUBD']
    
    FRONT_KEYWORDS_RE = re.compile('(^[Ll]$)|(^[Rr]$)|(^[Cc][Ll][Tt]$)')
    END_KEYWORDS_RE = re.compile('([Pp][Ll][Yy])|([Ss][Uu][Bb][Dd])')
    
    FRONT_KEYWORDS_ERROR = u'%s部分不在节点名的开头，或大小写错误\n' % ('/'.join(FRONT_KEYWORDS))
    FRONT_KEYWORDS_MULTI_ERROR = u'节点名中有多于一个%s存在\n' % ('/'.join(FRONT_KEYWORDS))
    END_KEYWORDS_ERROR = u'%s部分不在节点名的结尾，或大小写错误\n' % ('/'.join(END_KEYWORDS))
    END_KEYWORDS_MULTI_ERROR = u'节点名中有多于一个%s存在\n' % ('/'.join(END_KEYWORDS))
    LOWER_CASE_ERROR = u'除L/R/PLY/SUBD之外，节点名中仍有大写字母，或其他非法字符\n'
    MULTI_UNDERSCORE_ERROR = u'名字以下划线开头、结尾或有多于一个下划线连用/\n'
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查poly组下节点命名。"
        self.description = u"除L/R/PLY/SUBD之外，其余部分全部小写。L或R应出现在开头，且在整个名字中只应该出现一次；PLY或SUBD应出现在结尾，且在整个名字中只应该出现一次。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        #return

    @record_time(__file__)
    def run_check(self):

        result = u''
        try:
            #self.dialog.d_assets_info: current model asset info, 
            #e.g. keys: node, tank_file, task, publish_dir, node_name, version_dir, asset, etc
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                #print 'root: ', root
                if not pm.objExists(root):
                    return u'没有找到 ' + root.name()
                else:
                    poly_hi_all_descendents = pm.listRelatives(root + u'|poly', allDescendents = True, type = 'transform')
                    for descendent in poly_hi_all_descendents:
                        descendent = descendent.__str__().split('|')[-1]        #convert from nt.Transform to a string
                        descendent_splits = descendent.split('_')

                        #five boolean values, represent five types of errors
                        pass_underscore_check = self.check_underscore(descendent_splits)
                        descendent_splits = self.remove_blank_elem(pass_underscore_check,descendent_splits)

                        pass_frontkeyword_check, pass_multi_front_keywords_check, existing_frontkeywords = self.check_keywords(descendent_splits, StdCheck.FRONT_KEYWORDS_RE, 0)
                        descendent_splits = self.remove_unused_elem(pass_frontkeyword_check, existing_frontkeywords, descendent_splits)
                        
                        pass_endkeyword_check, pass_multi_end_keywords_check, existing_endkeywords = self.check_keywords(descendent_splits, StdCheck.END_KEYWORDS_RE, -1)
                        descendent_splits = self.remove_unused_elem(pass_endkeyword_check, existing_endkeywords, descendent_splits)
                        
                        pass_namelowercase_check = self.check_name_lowercase(descendent_splits)
                        
                        #organise checking result to a string
                        result += self.organise_output_infor(descendent, pass_underscore_check, pass_frontkeyword_check, pass_endkeyword_check, 
                                                             pass_multi_front_keywords_check, pass_multi_end_keywords_check,
                                                             pass_namelowercase_check)
            return result

        except:
            return traceback.format_exc()

    def organise_output_infor(self, descendent, pass_underscore_check, pass_frontkeyword_check, pass_endkeyword_check, 
                              pass_multi_front_keywords_check, pass_multi_end_keywords_check, 
                              pass_namelowercase_check):
        '''
        organise output information to the checking log.
        only show failure nodes and their error information
        '''
        if isinstance(descendent, str):
            descendent = descendent.decode('utf-8')
        descendent += u'\n'
        
        output = u''
        if not pass_underscore_check:
            output = self.joinString(output, descendent, StdCheck.MULTI_UNDERSCORE_ERROR)

        if not pass_frontkeyword_check:
            output = self.joinString(output, descendent, StdCheck.FRONT_KEYWORDS_ERROR)
        
        if not pass_endkeyword_check:
            output = self.joinString(output, descendent, StdCheck.END_KEYWORDS_ERROR)
            
        if not pass_multi_front_keywords_check:
            output = self.joinString(output, descendent, StdCheck.FRONT_KEYWORDS_MULTI_ERROR)
            
        if not pass_multi_end_keywords_check:
            output = self.joinString(output, descendent, StdCheck.END_KEYWORDS_MULTI_ERROR)
            
        if not pass_namelowercase_check:
            output = self.joinString(output, descendent, StdCheck.LOWER_CASE_ERROR)
            
        if output != u'':
            output += u'\n' 
        return output
    
    def joinString(self, output, node_name, error_info):
        '''
        combine a node and one of its error
        '''
        if node_name not in output:
            output += node_name
        output += u'......' + error_info
        
        return output
                

    def run_fix(self):
        '''Auto Fix'''
        unfixed_nodes = []
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                if not pm.objExists(root):
                    return u'没有找到' + root.name()
                else:
                    poly_hi_all_descendents = pm.listRelatives(root + u'|poly', allDescendents = True, type = 'transform')
                    for descendent in poly_hi_all_descendents:
                        descendent = descendent.__str__()       #convert from nt.Transform to a string
                        descendent_splits = descendent.split('_')
                        new_frontkeyword = ''
                        new_endkeyword = ''
                        
                        #check process
                        pass_underscore_check = self.check_underscore(descendent_splits)
                        descendent_splits = self.remove_blank_elem(pass_underscore_check, descendent_splits)    # fix redundant '_' 
                        
                        pass_frontkeyword_check, pass_multi_front_keywords_check, existing_frontkeywords = self.check_keywords(descendent_splits, StdCheck.FRONT_KEYWORDS_RE, 0)
                        descendent_splits = self.remove_unused_elem(pass_frontkeyword_check, existing_frontkeywords, descendent_splits)
                        #print 'existing_frontkeywords: ', existing_frontkeywords
                        #print 'descendent_splits1: ', descendent_splits
                        
                        pass_endkeyword_check, pass_multi_end_keywords_check, existing_endkeywords = self.check_keywords(descendent_splits, StdCheck.END_KEYWORDS_RE, -1)
                        descendent_splits = self.remove_unused_elem(pass_endkeyword_check, existing_endkeywords, descendent_splits)
                        #print 'existing_endkeywords: ', existing_endkeywords
                        #print 'descendent_splits2: ', descendent_splits
                        
                        pass_namelowercase_check = self.check_name_lowercase(descendent_splits)
                        
                        #fix process
                        descendent_splits = self.correct_multi_underscore(descendent_splits, pass_underscore_check)
                        new_frontkeyword, unfixed_nodes = self.correct_keyword(descendent, pass_frontkeyword_check, existing_frontkeywords, unfixed_nodes)
                        new_endkeyword, unfixed_nodes = self.correct_keyword(descendent, pass_endkeyword_check, existing_endkeywords, unfixed_nodes)
                        
                        #if all the name errors in the node can be fixed, then fix it, else, do nothing till finish all node checks.
                        if descendent not in unfixed_nodes:
                            if not pass_namelowercase_check or not pass_endkeyword_check or not pass_multi_end_keywords_check or \
                               not pass_frontkeyword_check or not pass_multi_front_keywords_check or not pass_underscore_check:
                                if not pass_namelowercase_check:
                                    descendent_splits = [elem.lower() for elem in descendent_splits]
                                if new_frontkeyword != '':
                                    descendent_splits.insert(0, new_frontkeyword)
                                if new_endkeyword != '':
                                    descendent_splits.append(new_endkeyword)
                                
                                #combine to a new name
                                newname = '_'.join(descendent_splits)
                                #print 'newname: ', newname
                                pm.rename(descendent, newname)
                            
            if len(unfixed_nodes) > 0:
                QtGui.QMessageBox.information(None, u'需手动修改的节点', u'以下节点名中有多个 L/R 或 PLY/SUBD 同时存在，请手动修改：\n%s' % ', \n'.join(unfixed_nodes))
                #print u'以下节点名中有多个L/R或PLY/SUBD同时存在，请手动修改：'
                
            return ''

        except:
            return traceback.format_exc()

        return
        
    def remove_unused_elem(self, pass_check, keywords, splits):
        '''
        if a keyword exists, remove it from the splits as a preparation for the next step
        '''
        if keywords != []:
            for keyword in keywords:
                #print 'remove keyword:', keyword
                splits.remove(keyword)          # remove all elems belong to front keywords
        return splits
    
    def remove_blank_elem(self, pass_underscore_check,splits):
        '''
        '''
        if not pass_underscore_check:
            filtered_splits = []
            for elem in splits:
                if elem != '':
                    filtered_splits.append(elem)
        else:
           filtered_splits = splits
        
        return filtered_splits    
    
    def check_name_lowercase(self, descendent_splits):
        '''
        after the two check
        all the elems in the descendent_splits MUST be lower case
        '''
        pass_namelowercase_check = True
        for elem in descendent_splits:
            if (not elem.islower()) and (not elem.isdigit()):
                pass_namelowercase_check = False
                break
            
        return pass_namelowercase_check
    
    def check_underscore(self, decendent_splits):
        '''
        '''
        pass_underscore_check = True
        if '' in decendent_splits:
            pass_underscore_check = False
            
        return pass_underscore_check
    
    
    def check_keywords(self, descendent_splits, keyword_pattern, compare_index):
        '''
        Args: descendent_splits: a list from a descendent string
              keyword_pattern: a re pattern
              compare_index: an int, define if a keyword exists in the descendent_splits, then where it is should be.
        
        1. if any elem from END_KEYWORDS exists in the splits, it MUST be the last elem of the descendent_splits
        2. if the elem is at the end, REMOVE it from the descendent_splits, for the preparation of the next check
        3. L/R can only have one in a name
        4. e.g. L_eye_L1, only change it case
        '''
        pass_keyword_check = True
        pass_multi_keyword_check = True
        existing_keywords = []                                    #in case more than one keywords exists
        
        for elem in descendent_splits:
            m = re.search(keyword_pattern, elem)
            if m is not None:       # if pattern exists
                existing_keywords.append(elem)
                if elem != elem.upper():                          #check if the elem is all upper
                    pass_keyword_check = False

                if elem != descendent_splits[compare_index]:      #check the location of the elem
                    pass_keyword_check = False
                
        if len(existing_keywords) > 1:
            pass_multi_keyword_check = False
            
        return pass_keyword_check, pass_multi_keyword_check, existing_keywords
    
    def correct_keyword(self, descendent, pass_check, keywords, unfixed_nodes):
        new_word = ''
        if not pass_check:
            if len(keywords) == 1:
                new_word = keywords[0].upper()
            elif len(keywords) > 1:
                if descendent not in unfixed_nodes:
                    unfixed_nodes.append(descendent)
        else:
            if len(keywords)== 1:
                new_word = keywords[0]
        return new_word, unfixed_nodes 

    def correct_multi_underscore(self, descendent_splits, pass_check):
        '''
        '''
        if not pass_check:
            descendent_splits = self.remove_blank_elem(pass_check, descendent_splits)
        #print 'new_descendent: ', descendent   
        return descendent_splits


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


