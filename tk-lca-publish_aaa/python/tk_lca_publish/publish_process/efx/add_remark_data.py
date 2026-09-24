# -*- coding:utf-8 -*-

import os
import traceback
import shutil
import re

import sys

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"Add remark"
        self.description = u"Add efx cache type and count"

    def proceed(self):    
        try:
            self.add_efx_remark()
        except:
            self.dialog.print_log(traceback.format_exc())

        return ''

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

    @staticmethod
    def count_efx_cache(efx_data,task_name=None):
        result={}
        for k,v in efx_data.items():
            if not v:
                continue
            if task_name and task_name!=k:
                continue
            result[k]=[]
            for kk,vv in v.items():
                elements=[]
                for path in vv:
                    version=path.split('/')[-3].split('.')[-1]
                    ele=path.split('/')[-2]+'.'+version
                    if ele not in elements:
                        elements.append(ele)

                if len(elements):
                    if kk!='exr':
                        result[k].append({'type':kk,'count':len(elements),'detail':elements})
                    else:
                        deep_exr_list=[e for e in elements if '_deep' in e]
                        result[k].append({'type':kk,'count':len(elements)-len(deep_exr_list),'detail':elements,'deep_count':len(deep_exr_list)})
        return result

    @staticmethod
    def convert_to_str(count_data):
        mark_content=''
        for m in count_data:
            detail_data=m.get('detail',[])
            if m.get('type')=='exr':
                none_deep=[d for d in detail_data if '_deep' not in d]
                len_none_deep=len(none_deep)
                if len_none_deep:
                    mark_content+='exr '+str(m.get('count'))+' '
                    mark_content+=' '.join(none_deep if 2>len_none_deep else none_deep[:1])
                    mark_content+=' ...' if 2<len_none_deep else ''
                
                if m.get('deep_count'):
                    deep_list=[d for d in detail_data if '_deep' in d]
                    len_deep_list=len(deep_list)
                    if len_deep_list:    
                        mark_content+='\ndeep_exr '+str(m.get('deep_count'))+' '
                        mark_content+=' '.join(deep_list if 2>len_deep_list else deep_list[:2])
                        mark_content+=' ...' if 2<len_deep_list else ''
            else:
                list_len=len(detail_data)

                mark_content+=m.get('type')+' '+str(m.get('count'))+' '
                mark_content+=' '.join(detail_data if 2>list_len else detail_data[:2])
                mark_content+=' ...' if 2<list_len else ''

            mark_content+='\n'

        return mark_content

    def add_efx_remark(self):
        shot = self.dialog.entity['name']
        proj = self.dialog.project['name']

        # sys.path.append('/mnt/utility/toolset/lib/production/pipeline')
        import production.pipeline.lcProdProj as lcpp
        
        ppinfo=lcpp.lcProdProj()
        ppinfo.setProj(proj)
        fx_raw_data=ppinfo.lcGetEfxAssets(shot)
        fx_any_data=ppinfo.analyzeFXAssets(fx_raw_data,set=False)
        count_data=StdProcess.count_efx_cache(fx_any_data,task_name=self.dialog.task['name'])
        mark_data_str=StdProcess.convert_to_str(count_data.get(self.dialog.task['name'],[]))
        if not mark_data_str:
            return

        task_data=self.dialog.sg.find('Task',
                            [
                                ['id','is',self.dialog.task['id']],
                                ['project', 'name_is',proj]
                            ],
                            ['sg_remark'])

        if task_data :
            if task_data[0].get('sg_remark'):
                old_desc=task_data[0]['sg_remark'].split(']')[-1]
                if not old_desc.startswith('\n'):
                    old_desc='\n'+old_desc
                self.dialog.sg.update('Task',
                                     self.dialog.task['id'], 
                                     {'sg_remark':'['+mark_data_str+']'+old_desc})
            else:
                self.dialog.sg.update('Task',
                                     self.dialog.task['id'], 
                                     {'sg_remark':'['+mark_data_str+']'})