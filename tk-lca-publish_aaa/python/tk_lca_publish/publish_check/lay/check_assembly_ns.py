# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description:
#
############################################
import traceback
import os
import pymel.core as pm
import production.mayautils.assembly as assutils


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查 Assembly Reference 节点名和命名空间。'
        self.description = u'检查 Assembly Reference 命名空间以资产名开头（可以带数字）；节点名为命名空间 + _AR 结尾。'
        self.auto_fix = True
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:

            illegal_names = []
            d_ar_info = {}
            for ar in pm.ls(type='assemblyReference'):
                if '|assets|lay|ars' in ar.longName():
                    continue
                ar_name = ar.name().split(':')[-1]
                par = ar.getParent()
                if par:
                    par_name = par.name().split(':')[:-1]
                    par_name = ':'.join(par_name)
                    if par_name and par_name not in ar.name():
                        illegal_names.append(u"节点 " + ar.name() + u": 名字应该包含 " + par_name + u"。")
                        continue
                ref_file = str(ar.getAttr("definition")).replace('\\', '/')
                if '/cty/' in ref_file: continue
                asset_name = os.path.basename(ref_file)[:-3]
                ar_namespace = ar.getAttr('repNamespace')
                d_ar_info[ar_name] = {'ref': ref_file, 'asset': asset_name, 'ns': ar_namespace, 'node': ar}

            # check scn node namespace and name
            illegal_names = []
            self.set_ns_dict = {}
            for ar_name, ar_info in d_ar_info.iteritems():
                ar_namespace = ar_info['ns']
                ar = ar_info['node']
                asset_name = ar_info['asset']
                if asset_name[-4:]=='_scn':
                    #print asset_name,ar_namespace,ar_name
                    if (asset_name+'_AR')!=ar_name:
                        # print asset_name,ar_namespace
                        illegal_names.append(u"节点 " + ar_name + u": 名字应该是 " + asset_name + u"_AR。")
                    if asset_name!=ar_namespace:
                        # print asset_name,ar_namespace
                        self.set_ns_dict[ar_namespace] = asset_name
                        illegal_names.append(u"节点 " + ar_name + u"层级 下面的 Assembly Reference 节点 命名空间应该是 " + asset_name + u" ，但场景中实际命名空间是 " + ar_namespace)
                    
            if illegal_names:
                return u"以下 scn 类型 的 Assembly Reference 的节点命名，或者命名空间不对:\n" + '\n'.join(illegal_names)
            
            # Check namespace field
            for ar_name, ar_info in d_ar_info.iteritems():
                ar_namespace = ar_info['ns']
                asset_name = ar_info['asset']
                if ar_namespace.rstrip('0123456789') != asset_name:
                    illegal_names.append(
                        u"节点 " + ar_name + u": 命名空间应该是 " + asset_name + u" ，或者是这之后带数字。现在是 " + ar_namespace)

            if illegal_names:
                return u"以下 Assembly Reference 的命名空间非法:\n" + '\n'.join(illegal_names)

            # Check node name
            illegal_names = []
            for ar_name, ar_info in d_ar_info.iteritems():
                ar_namespace = ar_info['ns']
                if ar_name != ar_namespace + '_AR':
                    illegal_names.append(u"节点 " + ar_name + u": 名字应该是 " + ar_namespace + u"_AR。")
                    continue

            if illegal_names:
                return u"以下 Assembly Reference 的节点命名非法:\n" + '\n'.join(illegal_names)

            # Check the real namespace in scene
            illegal_names = []
            for ar_name, ar_info in d_ar_info.iteritems():
                ar_namespace = ar_info['ns']
                ar = ar_info['node']
                l_nodes = pm.container(ar, q=True, nodeList=True)
                if not l_nodes:
                    continue

                tokens = l_nodes[0].split(':')
                if len(tokens) > 1 and tokens[-2] != ar_namespace:
                    self.set_ns_dict[tokens[-2]] = ar_namespace
                    illegal_names.append(
                        u"节点 " + ar_name + u": 命名空间是 " + ar_namespace + u" ，但场景中实际命名空间是 " + tokens[-2] + u"。")
                    continue

            if illegal_names:
                return u"以下 Assembly Reference 的节点命名非法:\n" + '\n'.join(illegal_names)
            


            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            import maya.cmds as cmds
            if self.set_ns_dict:
                self.run_fix_ns2(self.set_ns_dict)
            d_assets = {}
            l_ars = []
            for ar in pm.ls(type='assemblyReference'):
                if '|assets|lay|ars' in ar.longName():
                    continue
                # a debug filter
                # if not ar.name().startswith('game_g'):
                #    continue 
                ass = assutils.getOpenMayaAssemblyNode(ar.name())
                if ass.isTopLevel():
                    l_ars.append(ar)

            for ar in l_ars:
                ref_file = str(ar.getAttr("definition")).replace('\\', '/')
                asset_name = os.path.basename(ref_file)[:-3]
                ar_name = ar.name()
                ar_namespace = ar.getAttr('repNamespace')
                if not d_assets.has_key(asset_name):
                    d_assets[asset_name] = {'good': [], 'bad': []}
                if ar_namespace.rstrip('0123456789') != asset_name:
                    d_assets[asset_name]['bad'].append(ar)
                else:
                    if ar_name == ar_namespace + '_AR':
                        d_assets[asset_name]['good'].append(ar_namespace)
                    else:
                        ar.rename(ar_namespace + '_AR')
                        if ar.name() == ar_namespace + '_AR':
                            print ar_name, '>', ar_namespace + '_AR'
                            d_assets[asset_name]['good'].append(ar_namespace)
                        else:
                            d_assets[asset_name]['bad'].append(ar)

            for asset_name, d_asset_name in d_assets.iteritems():
                if len(d_asset_name['bad']) > 0:
                    print asset_name, len(d_asset_name['bad'])
                    for ar in d_asset_name['bad']:
                        old_ns = ar.getAttr('repNamespace')
                        old_name = ar.name()
                        l_existing_ns = pm.namespaceInfo(listOnlyNamespaces=True, recurse=False)
                        i = 0
                        new_ns = asset_name
                        while new_ns in l_existing_ns or new_ns in d_asset_name['good']:
                            i += 1
                            new_ns = asset_name + str(i)
                        pm.lockNode(ar, lock=0)
                        ar.setAttr('repNamespace', l=False)
                        ar.setAttr('repNamespace', new_ns)
                        if new_ns == ar.getAttr('repNamespace'):
                            ar.rename(new_ns + '_AR')
                            if new_ns + '_AR' == ar.name():
                                d_asset_name['good'].append(new_ns)
                                print old_name, '>', new_ns + '_AR', '>', ar.name(), '\n'
                            else:
                                print 'Failed to fix (name):', old_name, '.\n'
                        else:
                            print 'Failed to fix (namespace):', old_name, '.\n'

            for ar in l_ars:
                ar_namespace = ar.getAttr('repNamespace')
                l_nodes = pm.container(ar, q=True, nodeList=True)
                if not l_nodes:
                    continue

                tokens = l_nodes[0].split(':')
                if len(tokens) > 1 and tokens[-2] != ar_namespace:
                    pm.select(ar)
                    new_ar = pm.duplicate(rr=True)[0]
                    pm.delete(ar)
                    l_nodes_new = pm.container(new_ar, q=True, nodeList=True)
                    new_ar_name = l_nodes_new[0].split(':')[-2]
                    new_ar.rename(new_ar_name + '_AR')

            # can b70lvweidang temp solution, can delete later
            import maya.cmds as cmds
            b70_scn_no_use = [u'can_reed_b697_AR', u'can_reed_b541_AR', u'can_reed_a702_AR', u'can_reed_a697_AR',
                              u'can_reed_a609_AR', u'can_reed_c670_AR', u'can_reed_c580_AR', u'can_reed_b727_AR',
                              u'can_reed_b663_AR', u'can_reed_c698_AR', u'can_reed_c585_AR', u'can_reed_c523_AR',
                              u'can_reed_b729_AR', u'can_reed_b667_AR', u'can_reed_b595_AR', u'can_reed_a739_AR',
                              u'can_reed_c680_AR', u'can_reed_c532_AR', u'can_reed_c522_AR', u'can_reed_b539_AR',
                              u'can_reed_a735_AR', u'can_reed_a718_AR', u'can_reed_a717_AR', u'can_reed_a673_AR',
                              u'can_reed_a601_AR', u'can_reed_a549_AR', u'can_reed_c673_AR', u'can_reed_c589_AR',
                              u'can_reed_c588_AR', u'can_reed_c554_AR', u'can_reed_c533_AR', u'can_reed_a689_AR',
                              u'can_reed_c684_AR', u'can_reed_b592_AR', u'can_reed_a687_AR', u'can_reed_a596_AR',
                              u'can_reed_a562_AR', u'can_reed_a521_AR', u'can_reed_c556_AR', u'can_reed_c542_AR',
                              u'can_reed_b582_AR', u'can_reed_a614_AR', u'can_reed_c688_AR', u'can_reed_b724_AR',
                              u'can_reed_a738_AR', u'can_reed_a701_AR', u'can_reed_a688_AR', u'can_reed_a675_AR',
                              u'can_reed_a602_AR', u'can_reed_a595_AR', u'can_reed_c683_AR', u'can_reed_b597_AR',
                              u'can_reed_b584_AR', u'can_reed_b572_AR', u'can_reed_b542_AR', u'can_reed_b540_AR',
                              u'can_reed_a550_AR', u'can_reed_c567_AR', u'can_reed_b743_AR', u'can_reed_b672_AR',
                              u'can_reed_b585_AR', u'can_reed_a729_AR', u'can_reed_c660_AR', u'can_reed_c655_AR',
                              u'can_reed_c528_AR', u'can_reed_b742_AR', u'can_reed_b740_AR', u'can_reed_b737_AR',
                              u'can_reed_b734_AR', u'can_reed_b710_AR', u'can_reed_b574_AR', u'can_reed_b547_AR',
                              u'can_reed_a669_AR', u'can_reed_c520_AR', u'can_reed_c490_AR', u'can_reed_b598_AR',
                              u'can_reed_b545_AR', u'can_reed_c689_AR', u'can_reed_c685_AR', u'can_reed_c676_AR',
                              u'can_reed_c535_AR', u'can_reed_b836_AR', u'can_reed_b744_AR', u'can_reed_b708_AR',
                              u'can_reed_b695_AR', u'can_reed_b680_AR', u'can_reed_b661_AR', u'can_reed_b596_AR',
                              u'can_reed_b580_AR', u'can_reed_b554_AR', u'can_reed_b543_AR', u'can_reed_a557_AR',
                              u'can_reed_a528_AR', u'can_reed_c665_AR', u'can_reed_c650_AR', u'can_reed_c540_AR',
                              u'can_reed_c489_AR', u'can_reed_b706_AR', u'can_reed_b583_AR', u'can_reed_b549_AR',
                              u'can_reed_a605_AR', u'can_reed_a603_AR', u'can_reed_a552_AR', u'can_reed_c687_AR',
                              u'can_reed_c590_AR', u'can_reed_c570_AR', u'can_reed_b728_AR', u'can_reed_b555_AR',
                              u'can_reed_a570_AR', u'can_reed_a568_AR', u'can_reed_a529_AR', u'can_reed_a347_AR',
                              u'can_reed_a346_AR', u'can_reed_c682_AR', u'can_reed_b726_AR', u'can_reed_b696_AR',
                              u'can_reed_a594_AR', u'can_reed_a566_AR', u'can_reed_c651_AR', u'can_reed_b837_AR',
                              u'can_reed_b745_AR', u'can_reed_b701_AR', u'can_reed_b694_AR', u'can_reed_a827_AR',
                              u'can_reed_a611_AR', u'can_reed_a606_AR', u'can_reed_c668_AR', u'can_reed_c649_AR',
                              u'can_reed_c581_AR', u'can_reed_c530_AR', u'can_reed_c491_AR', u'can_reed_b665_AR',
                              u'can_reed_a742_AR', u'can_reed_a719_AR', u'can_reed_a569_AR', u'can_reed_c587_AR',
                              u'can_reed_b741_AR', u'can_reed_b707_AR', u'can_reed_b670_AR', u'can_reed_b669_AR',
                              u'can_reed_b599_AR', u'can_reed_a725_AR', u'can_reed_c674_AR', u'can_reed_c584_AR',
                              u'can_reed_c577_AR', u'can_reed_a797_AR', u'can_reed_a518_AR', u'can_reed_c696_AR',
                              u'can_reed_c693_AR', u'can_reed_c657_AR', u'can_reed_c593_AR', u'can_reed_c583_AR',
                              u'can_reed_b805_AR', u'can_reed_b703_AR', u'can_reed_a556_AR', u'can_reed_c697_AR',
                              u'can_reed_c666_AR', u'can_reed_c648_AR', u'can_reed_c555_AR', u'can_reed_b735_AR',
                              u'can_reed_b709_AR', u'can_reed_b581_AR', u'can_reed_b573_AR', u'can_reed_b552_AR',
                              u'can_reed_b548_AR', u'can_reed_a724_AR', u'can_reed_a723_AR', u'can_reed_a722_AR',
                              u'can_reed_a564_AR', u'can_reed_a559_AR', u'can_reed_a312_AR', u'can_reed_c671_AR',
                              u'can_reed_c574_AR', u'can_reed_b736_AR', u'can_reed_b705_AR', u'can_reed_b586_AR',
                              u'can_reed_a734_AR', u'can_reed_a699_AR', u'can_reed_a555_AR', u'can_reed_a519_AR',
                              u'can_reed_c571_AR', u'can_reed_c286_AR', u'can_reed_a714_AR', u'can_reed_a604_AR',
                              u'can_reed_c586_AR', u'can_reed_b590_AR', u'can_reed_a599_AR', u'can_reed_c672_AR',
                              u'can_reed_c659_AR', u'can_reed_c488_AR', u'can_reed_a737_AR', u'can_reed_a554_AR',
                              u'can_reed_b683_AR', u'can_reed_a743_AR', u'can_reed_a711_AR', u'can_reed_a558_AR',
                              u'can_reed_c700_AR', u'can_reed_b748_AR', u'can_reed_b662_AR', u'can_reed_a619_AR',
                              u'can_reed_a608_AR', u'can_reed_a593_AR', u'can_reed_a520_AR', u'can_reed_b723_AR',
                              u'can_reed_b588_AR', u'can_reed_b546_AR', u'can_reed_a713_AR', u'can_reed_a700_AR',
                              u'can_reed_a698_AR', u'can_reed_a671_AR', u'can_reed_a670_AR', u'can_reed_a613_AR',
                              u'can_reed_a610_AR', u'can_reed_c669_AR', u'can_reed_c576_AR', u'can_reed_c557_AR',
                              u'can_reed_c537_AR', u'can_reed_c524_AR', u'can_reed_b747_AR', u'can_reed_b720_AR',
                              u'can_reed_b702_AR', u'can_reed_b698_AR', u'can_reed_b553_AR', u'can_reed_b551_AR',
                              u'can_reed_b273_AR', u'can_reed_a721_AR', u'can_reed_a712_AR', u'can_reed_a607_AR',
                              u'can_reed_c654_AR', u'can_reed_c525_AR', u'can_reed_b681_AR', u'can_reed_b668_AR',
                              u'can_reed_a672_AR', u'can_reed_a616_AR', u'can_reed_a598_AR', u'can_reed_a597_AR',
                              u'can_reed_a551_AR', u'can_reed_c782_AR', u'can_reed_c658_AR', u'can_reed_c579_AR',
                              u'can_reed_b749_AR', u'can_reed_b660_AR', u'can_reed_b589_AR', u'can_reed_b587_AR',
                              u'can_reed_b556_AR', u'can_reed_a732_AR', u'can_reed_a715_AR', u'can_reed_a612_AR',
                              u'can_reed_a575_AR', u'can_reed_c592_AR', u'can_reed_c534_AR', u'can_reed_c521_AR',
                              u'can_reed_b664_AR', u'can_reed_b666_AR', u'can_reed_b593_AR', u'can_reed_a620_AR',
                              u'can_reed_c569_AR', u'can_reed_c531_AR', u'can_reed_b722_AR', u'can_reed_b699_AR',
                              u'can_reed_b671_AR', u'can_reed_b550_AR', u'can_reed_a720_AR', u'can_reed_c694_AR',
                              u'can_reed_c591_AR', u'can_reed_c578_AR', u'can_reed_a716_AR', u'can_reed_a696_AR',
                              u'can_reed_c575_AR', u'can_reed_b591_AR', u'can_reed_c675_AR', u'can_reed_a740_AR',
                              u'can_reed_a686_AR', u'can_reed_a676_AR', u'can_reed_c681_AR', u'can_reed_c526_AR',
                              u'can_reed_b746_AR', u'can_reed_b738_AR', u'can_reed_b704_AR', u'can_reed_b682_AR',
                              u'can_reed_a736_AR', u'can_reed_c699_AR', u'can_reed_c695_AR', u'can_reed_b721_AR',
                              u'can_reed_b700_AR', u'can_reed_b512_AR', u'can_reed_a744_AR', u'can_reed_a731_AR',
                              u'can_reed_a617_AR', u'can_reed_a615_AR', u'can_reed_a565_AR', u'can_reed_a563_AR',
                              u'can_reed_c686_AR', u'can_reed_c656_AR', u'can_reed_c573_AR', u'can_reed_c536_AR',
                              u'can_reed_b594_AR', u'can_reed_b544_AR', u'can_reed_a733_AR', u'can_reed_a618_AR',
                              u'can_reed_a567_AR', u'can_reed_a553_AR', u'can_reed_c568_AR', u'can_reed_c527_AR',
                              u'can_reed_b739_AR', u'can_reed_b725_AR', u'can_reed_b659_AR', u'can_reed_a741_AR',
                              u'can_reed_a730_AR', u'can_reed_a674_AR', u'can_reed_a600_AR', u'can_reed_c667_AR',
                              u'can_reed_c582_AR', u'can_reed_c572_AR', u'can_reed_c783_AR']
            scn_obj = cmds.ls("|assets|scn|b70luweidang_scn_AR", dag=True)
            for sel in b70_scn_no_use:
                # b70_scn_no_use.append(sel)
                if cmds.objExists(sel) and (sel in scn_obj):
                    cmds.delete(sel)
                else:
                    pass

            return ''
        except:
            return traceback.format_exc()


    def run_fix_ns2(self, set_ns_dict):
        import maya.cmds as cmds

        if not set_ns_dict:
            return

        # 1. 获取场景中所有的命名空间绝对路径 (用于匹配短名字)
        all_namespaces = cmds.namespaceInfo(":", listOnlyNamespaces=True, recurse=True) or []
        # 确保路径以冒号开头
        all_namespaces = [ns if ns.startswith(":") else ":" + ns for ns in all_namespaces]

        # 2. 获取场景中所有的 assemblyReference 节点
        # 因为 Assembly 拥有的命名空间必须通过修改节点属性来改名
        assembly_nodes = cmds.ls(type='assemblyReference')

        # Python 2.7 使用 iteritems 遍历字典
        for key, data in set_ns_dict.iteritems():

            # --- 步骤 A: 找到 key（原名字）的完整绝对路径 ---
            full_key_path = None
            for ns in all_namespaces:
                # 匹配路径末尾的名字
                if ns.split(":")[-1] == key:
                    full_key_path = ns
                    break

            if not full_key_path:
                print "Skip: Could not find namespace '%s' in scene." % key
                continue

            # --- 步骤 B: 判断该空间是否属于 Assembly 节点 ---
            short_key = full_key_path.lstrip(":")
            target_assembly = None

            for node in assembly_nodes:
                if cmds.attributeQuery("namespace", node=node, exists=True):
                    # 检查 assembly 节点的 namespace 属性是否匹配
                    if cmds.getAttr(node + ".namespace") == short_key:
                        target_assembly = node
                        break

            # --- 步骤 C: 执行改名操作 ---
            if target_assembly:
                # 如果是 Assembly 空间：直接修改节点的属性，不要用 namespace(rename)
                try:
                    cmds.setAttr(target_assembly + ".namespace", data, type="string")
                    print "Success: Updated Assembly namespace [%s] to '%s'" % (target_assembly, data)
                except Exception as e:
                    print "Error: Failed to set assembly attribute: %s" % str(e)
            else:
                # 如果是普通空间：使用重命名逻辑
                try:
                    # 检查目标名字 data 是否已存在，防止 rename 冲突
                    target_exists = False
                    full_data_path = ""
                    for ns in all_namespaces:
                        if ns.split(":")[-1] == data:
                            target_exists = True
                            full_data_path = ns
                            break

                    if target_exists:
                        # 如果目标已存在，将 key 里的东西移到 data 里，不删物体
                        print "Target '%s' exists, merging content..." % data
                        cmds.namespace(moveNamespace=(full_key_path, full_data_path), force=True)
                        # 移动完后，旧空间变空，尝试删除它
                        try:
                            cmds.namespace(removeNamespace=full_key_path)
                        except:
                            # 如果是受限空间删不掉，至少内容已经移走了
                            pass
                    else:
                        # 正常重命名 (第一个参数用绝对路径，第二个参数用新的短名)
                        cmds.namespace(rename=(full_key_path, data))
                        print "Success: Renamed namespace %s -> %s" % (full_key_path, data)

                except Exception as e:
                    print "Error: Failed to rename namespace %s: %s" % (full_key_path, str(e))

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
