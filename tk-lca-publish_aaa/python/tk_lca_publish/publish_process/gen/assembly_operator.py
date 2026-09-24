# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import os
import math
import shutil
import traceback
import pymel.core as pm

class AssemblyOperator():
    """
        class for assembly operation, the prerequisite is that all reference nodes reside under namespace, otherwise this
        class will likely return false result, so be used with caution
    """

    def __init__(self):
        self.ref_all = []
        self.ref_mod = []
        self.ref_asb = []
        self.intermediate_ctrl = []
        self.asb_ctrl_path = ''
        self.update()

    def update(self):
        '''
        update ref_all, ref_mod and ref_asb
        '''
        # get all top-level reference nodes
        self.ref_all = pm.ls('*:master', rn=True, long=True)
        # filter model/rig master
        self.ref_mod = filter(None, [ m for m in [r for r in self.ref_all if [p for p in r.getChildren() if 'poly' in str(p)] ] if m.isChildOf('|master|asb') ])
        # filter assembly master
        self.ref_asb = filter(None, [ a for a in [r for r in self.ref_all if [p for p in r.getChildren() if 'asb' in str(p)] ] if a.isChildOf('|master|asb') ])
        self.intermediate_ctrl = self.list_intermediate_ctrl()
        # grab asb controls path
        self.asb_ctrl_path = '/'.join(os.path.dirname(__file__).split('/')[:-1]) + '/mod_asb/'
        if not os.path.isfile(self.asb_ctrl_path+'asb_global_control.ma'):
            self.asb_ctrl_path = os.path.dirname(__file__) + '/'
            if not os.path.isfile(self.asb_ctrl_path+'asb_global_control.ma'):
                self.asb_ctrl_path = ''

    def toPyNode(self, node):
        if isinstance(node, type('')):
            if pm.objExists(node):
                return pm.PyNode(node)
            else:
                return None
        else:
            return node

    def listAllReferences(self):
        '''
        list all top-level reference nodes, child reference would be discarded
        '''
        return self.ref_all

    def listModReferences(self):
        '''
        list all top-level reference nodes of models and rigging, child reference would be discarded
        '''
        return self.ref_mod

    def listAsbReferences(self):
        '''
        list all top-level reference nodes of assembly, child reference would be discarded
        '''
        return self.ref_asb

    def getNamespace(self, node, wcn=False):
        '''
        get namespace of given node, with leading string ':'
        option: wcn=False, strip tailing number
        '''
        try:
            ns_fn = lambda x: x if x.startswith(':') else ':'+x
            ns = ns_fn( pm.referenceQuery( node, namespace=True ) ).replace(':master', '')
            if wcn:
                # strip tail number
                while ns[-1].isdigit():
                    ns = ns[:-1]
            return ns
        except:
            return None

    def findGlobalCtrl(self, obj):
        '''
        return global_ctrl under given referenced master group
        '''
        # obj may be a unloaded pynode
        if not obj:
            if pm.objExists(str(obj)):
                obj = self.toPyNode(str(obj))
            else:
                return None

        ns = None
        try:
            ns = self.getNamespace(obj)
        except:
            return None

        if not ns or ns == ':':
            return None

        if pm.objExists(ns + ':global_ctrl'):
            return pm.PyNode(ns+':global_ctrl')

        return None

    def findRootCtrl(self, obj):
        '''
        return root_ctrl under given referenced master group
        '''
        # obj may be a unloaded pynode
        if not obj:
            if pm.objExists(str(obj)):
                obj = self.toPyNode(str(obj))
            else:
                return None

        ns = None
        try:
            ns = self.getNamespace(obj)
        except:
            return None

        if not ns or ns == ':':
            return None

        if pm.objExists(ns + ':root_ctrl'):
            return pm.PyNode(ns+':root_ctrl')

        return None

    def findPoly(self, obj):
        '''
        return the poly group under given master node
        '''
        # obj may be a unloaded pynode
        if not obj:
            if pm.objExists(str(obj)):
                obj = self.toPyNode(str(obj))
            else:
                return None

        ns = None
        try:
            ns = self.getNamespace(obj)
        except:
            return None

        if not ns or ns == ':':
            return None

        if pm.objExists(ns + ':poly'):
            return pm.PyNode(ns+':poly')

        return None

    def findAsb(self, obj):
        '''
        return the asb group under given master node
        '''
        if obj.type() != 'transform':
            print 'Error on findAsb(obj): please input a master node'
            return None
        return [g for g in obj.getChildren(type='transform') if 'asb' in str(g)]

    def unlockTransform(self, obj, attributes=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'globalScale']):
        try:
            for attr in attributes:
                if obj.hasAttr(attr):
                    obj.setAttr(attr, lock=False)
        except:
            print str(obj)+' - Error on unlockTransform()'

    def lockTransform(self, obj, attributes=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'globalScale']):
        try:
            for attr in attributes:
                if obj.hasAttr(attr):
                    obj.setAttr(attr, lock=True)
        except:
            print str(obj)+' - Error on lockTransform()'

    def setAttrState(self, obj, attributes=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], lock=True, keyable=False, channelBox=False):
        try:
            for attr in attributes:
                if obj.hasAttr(attr):
                    obj.setAttr(attr, lock=lock, keyable=keyable, channelBox=channelBox)
        except:
            print str(obj)+'Error on setAttrState()'

    def getBoundingBox(self, g_ctrl, geo):
        '''
        return bbox in the identity position, by given global_ctrl and poly or asb
        '''
        if g_ctrl and g_ctrl.type()=='transform':
            tr = g_ctrl.getTranslation()
            rot = g_ctrl.getRotation()
        else:
            tr = pm.dt.Vector([0,0,0])
            rot = pm.dt.EulerRotation([0,0,0])

        gScaleBool = g_ctrl.hasAttr('globalScale')
        if gScaleBool:
            gScale = g_ctrl.attr('globalScale').get()

        try:
            g_ctrl.setTranslation([0,0,0])
            g_ctrl.setRotation([0,0,0])
            if gScaleBool:
                g_ctrl.attr('globalScale').set(1)
        except:
            print 'getBoundingBox Error: unable to set translate, rotation and globalScale attr'
            pass

        if geo and geo.type()=='transform':
            bbox = geo.boundingBox()
        else:
            bbox = pm.dt.BoundingBox([0,0,0],[0,0,0])

        try:
            g_ctrl.setTranslation(tr)
            g_ctrl.setRotation(rot)
            if gScaleBool:
                g_ctrl.attr('globalScale').set(gScale)
        except:
            print 'getBoundingBox Error: unable to set translate, rotation and globalScale attr'
            pass

        return bbox

    def list_intermediate_ctrl(self):
        '''
        list intermediate_ctrl under every master group of top referenced mod and rig, exclude child reference
        note: this method deletes any intermediate_ctrl under root space
        '''
        int_exists = []
        # get intermediate_ctrl rest under root space with and without namespace
        int_exists.extend( pm.ls('|*intermediate_ctrl', type='transform') )
        int_exists.extend( pm.ls('|*:*intermediate_ctrl', type='transform') )
        if int_exists:
            for i in int_exists:
                try:
                    pm.lockNode( i, lock=False)
                    pm.delete( i )
                except:
                    pass
        int_ctrl = pm.ls('*:intermediate_ctrl', long=True, type='transform')
        illegal_ctrl = []
        for ctrl in int_ctrl:
            if not [ c for c in ctrl.getChildren() if 'intermediate_root_ctrl' in str(c) ]:
                illegal_ctrl.append(ctrl)
        for ctrl in illegal_ctrl:
            int_ctrl.remove(ctrl)
        return filter(None, int_ctrl)

    def list_all_intermediate_root_ctrl(self):
        '''
        list all intermediate_root_ctrl.
        This method can be used to set globalScale attribute on the intermediate_root_ctrl node
        '''
        self.update()
        root_ctrl = []
        for ctrl in self.ref_mod+self.ref_asb:
            root_ctrl.extend( pm.ls(ctrl.name()+'|*:intermediate_ctrl|*:intermediate_root_ctrl', type='transform') )
        return filter(None, root_ctrl)

    def list_asb_global_ctrl(self):
        '''
        list global_ctrl under every referenced assembly
        '''
        asb_g_ctrl = []
        for asb in self.ref_asb:
            asb_g_ctrl.append( self.findGlobalCtrl(asb) )
        return filter(None, asb_g_ctrl)

    def copyTransformation(self, a, b):
        '''
        copy transformation from a to b
        '''
        try:
            b.setTranslation( a.getTranslation() )
            b.setRotation( a.getRotation() )
        except:
            print 'copyTransformation Error: unable to set translate, rotation'
        #try:
        #    b.setScale( a.getScale() )
        #except:
        #    pass

    def getTransformation(self, a, space='object'):
        # a may be a unloaded pynode
        if not a:
            if pm.objExists(str(a)):
                a = self.toPyNode(str(a))
            else:
                return {}
        try:
            if a.type()!='transform':
                return {}
        except:
            return {}
        tran = {}
        txyz = a.getTranslation(space=space)
        rxyz = a.getRotation(space=space)
        sxyz = a.getScale()
        tran['tx'] = txyz[0] if a.hasAttr('tx') else None
        tran['ty'] = txyz[1] if a.hasAttr('ty') else None
        tran['tz'] = txyz[2] if a.hasAttr('tz') else None
        tran['rx'] = rxyz[0] if a.hasAttr('rx') else None
        tran['ry'] = rxyz[1] if a.hasAttr('ry') else None
        tran['rz'] = rxyz[2] if a.hasAttr('rz') else None
        tran['sx'] = sxyz[0] if a.hasAttr('sx') else None
        tran['sy'] = sxyz[1] if a.hasAttr('sy') else None
        tran['sz'] = sxyz[2] if a.hasAttr('sz') else None
        tran['globalScale'] = a.attr('globalScale').get() if a.hasAttr('globalScale') else None

        return tran

    def setTransformation(self, a, tran):
        # a may be a unloaded pynode
        if not a:
            if pm.objExists(str(a)):
                a = self.toPyNode(str(a))
            else:
                return {}
        try:
            if a.type()!='transform':
                return
        except:
            return
        if not tran:
            try:
                for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                    if a.hasAttr(attr):
                        a.attr(attr).set(0)
                if a.hasAttr('globalScale'):
                    a.attr('globalScale').set(1)
                for attr in ['sx', 'sy', 'sz']:
                    if a.hasAttr(attr):
                        a.attr(attr).set(1)
            except:
                pass
            return
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'globalScale']:
            if a.hasAttr(attr) and tran.has_key(attr) and tran[attr]!=None:
                lockState = a.attr(attr).isLocked()
                if not a.isReferenced():
                    a.setAttr(attr, lock=False)
                try:
                    a.attr(attr).set(tran[attr])
                except:
                    pass
                if not a.isReferenced():
                    a.setAttr(attr, lock=lockState)

    def getReferenceFile(self, node):
        '''
        This give FileReference, instead of string path
        '''
        file_ref = pm.FileReference(str(node))
        if file_ref.namespace == ':':
            parent_refNode = pm.referenceQuery(file_ref.refNode, rfn=True, parent=True)
            return self.getReferenceFile( parent_refNode )
        return file_ref

    def getNonReference(self, top):
        '''
        get non-reference node under given top
        option: top=None
        '''
        children = pm.listRelatives(top, c=True, type='transform')
        trans = []
        for c in children:
            if pm.referenceQuery(c, inr=True):
                continue
            elif c.name().endswith(':master') and pm.referenceQuery(c, inr=True):
                continue
            elif c.name().endswith('rig') or c.name().endswith('asb'):
                continue
            else:
                trans.append(c)
                trans.extend( self.getNonReference(c) )
        return trans

    def getChildReferenceNodes(self, ref_node):
        child_ref_node = []
        tmp =  pm.referenceQuery(ref_node, child=True, rfn=True)
        if tmp:
            child_ref_node.extend( tmp )
            child_ref_node.extend( self.getChildReferenceNodes(tmp) )
        return child_ref_node

    def deleteReferenceEdits(self, node):
        file_ref = self.getReferenceFile(node)
        ref_node = file_ref.refNode
        child_ref_nodes = self.getChildReferenceNodes( ref_node )
        non_ref = self.getNonReference(node)
        # delete non-referenced node before deleting reference edits
        try:
            if non_ref:
                pm.delete(non_ref)
        except:
            pm.warning('failed to delete non-referenced node under ' +str(node)+ 'before deleting reference edits: '+'\n'.join(non_ref) )
            return False
        # do deletion of reference edits
        # unload reference first
        try:
            if file_ref.isLoaded():
                file_ref.unload()
        except:
            pm.warning('failed to unload reference for'+str(node))
            return False
        # delete reference edits
        try:
            pm.referenceEdit(ref_node, removeEdits=True, successfulEdits=True)
            pm.referenceEdit(ref_node, removeEdits=True, failedEdits=True)
            for c in child_ref_nodes:
                pm.referenceEdit(c, removeEdits=True, successfulEdits=True)
                pm.referenceEdit(c, removeEdits=True, failedEdits=True)
        except:
            pm.warning('failed to delete reference edits for '+str(node))
            if not file_ref.isLoaded():
                try:
                    file_ref.load()
                except:
                    pass
            return False
        # reload reference
        if not file_ref.isLoaded():
            try:
                file_ref.load()
            except:
                pm.warning( 'failed to reload reference file after deletion of reference edits: \n'+str(ref_node) + '\n' + str(file_ref) )
                return False
        return True

    def add_intermediate_ctrl(self):
        '''
        add intermediate control for mod and rig asset(not asb assets) in assembly group. This is necessary for moving assembly all in one while
        keep capability of individuals' transformation.
        Note: this method should not be called independently, use add_ctrl() which call this method and do other setups
        '''
        mod_ctrl_path = self.asb_ctrl_path + 'intermediate_mod.ma'
        asb_ctrl_path = self.asb_ctrl_path + 'intermediate_asb.ma'
        if not os.path.isfile(mod_ctrl_path) or not os.path.isfile(asb_ctrl_path):
            print 'Can not find '+mod_ctrl_path
            print 'Can not find '+asb_ctrl_path
            return False

        #delete any existing intermediate ctrl under root world with and without namespace
        root_int_exists = []
        root_int_exists.extend( pm.ls('|*intermediate_ctrl', type='transform') )
        root_int_exists.extend( pm.ls('|*:*intermediate_ctrl', type='transform') )
        for rie in root_int_exists:
            try:
                pm.lockNode(rie, lock=False)
                pm.delete(rie)
            except:
                print 'Intermediate Ctrl Warning: '+str(rie)+' can not be deleted before proceeding, ignored.'

        for ref in self.ref_mod + self.ref_asb:
            # here we assume there are rig, poly or asb group under every master transform
            # delete ctrl if it exists, then create new one

            ref_string = str(ref)

            int_exists = [n for n in ref.getChildren() if 'intermediate_ctrl' in str(n)]
            if int_exists:
                for i in int_exists:
                    try:
                        pm.lockNode( i, lock=False)
                        pm.delete( i )
                    except:
                        print 'Intermediate Ctrl Warning: '+str(i)+' can not be deleted before proceeding, ignored.'
                        #self.intermediate_ctrl = self.list_intermediate_ctrl()
                        continue

            # create intermediate controls
            ns_fn = lambda x: x if x.startswith(':') else ':'+x
            ns = ns_fn( pm.referenceQuery( ref, namespace=True ) )
            current_ns = ns_fn( pm.namespaceInfo(cur=True) )
            # set namespace, so everything newly created is under this namespace
            pm.namespace(set=ns)
            ctrl = None
            try:
                if ref in self.ref_mod:
                    ctrl = pm.importFile( mod_ctrl_path, returnNewNodes=True )
                else:
                    ctrl = pm.importFile( asb_ctrl_path, returnNewNodes=True )
            except:
                print 'Error on add_intermediate_ctrl() when import intermediate_*.ma file'
                self.safeDelete(ctrl)
                continue
            #pm.namespace(set=current_ns)

            # grab global_ctrl, root_ctrl and bbox of poly group
            g_ctrl = self.findGlobalCtrl( ref )
            g_ctrl_string = str(g_ctrl)
            geo = self.findPoly( ref ) if ref in self.ref_mod else self.findAsb( ref )
            geo_string = str(geo)

            ### store transformation of global_ctrl, delete reference edits to force ref back to original
            g_ctrl_transformation = self.getTransformation(g_ctrl)
            ref_parent = pm.listRelatives(ref, parent=True)
            file_ref = self.getReferenceFile(ref)
            delete_ref_bool = True
            if ref_parent:
                if pm.referenceQuery(ref_parent, inr=True):
                    delete_ref_bool = False
                else:
                    ref_parent = ref_parent[0]

            # if this is rig asset, then we should not delete the reference edits, because that the artist could hide some parts of model by rigging control
            if 'rig.rigging' in str(file_ref.path):
                delete_ref_bool = False

            # Add Fucking exclusion for tuk_tuk_bomb asset, because that they add deformers in the asb file therefore we can't delete the reference edits, and that freaky requirement asked by the mad animation
            # Never mind, just add this fucking exclusion
            if os.path.basename(pm.sceneName()).split('.')[0] == 'tuk_tuk_bomb':
                delete_ref_bool = False

            # delete reference edits
            if not delete_ref_bool or not self.deleteReferenceEdits(ref):
                # if delete reference edits failed, we move the g_ctrl to the center of world
                if not file_ref.isLoaded():
                    file_ref.load()
                self.setTransformation(g_ctrl, {})
            # recover of pynode object, this is necessary after deletion of edits
            if delete_ref_bool:
                ref = self.toPyNode( ref_string )
                g_ctrl = self.toPyNode( g_ctrl_string )
                geo = self.toPyNode( geo_string )
            # ref will get back to the root after deleting of edits, so parent it to original group
            if delete_ref_bool and ref_parent and not self.toPyNode(ref).isChildOf(ref_parent):
                try:
                    pm.parent(ref, ref_parent)
                except:
                    print 'Error on add_intermediate_ctrl() when trying to parent '+str(ref)+' to '+str(ref_parent)
                    self.safeDelete(ctrl)
                    continue

            # parent intermediate control under ref
            try:
                pm.parent(ctrl[0], ref)
            except:
                print 'Error on add_intermediate_ctrl() when trying to parent '+str(ctrl[0])+' under '+str(ref)
                self.setTransformation(g_ctrl, g_ctrl_transformation)
                self.safeDelete(ctrl)
                continue
            int_ctrl = ctrl[0]
            int_root_ctrl = ctrl[2]

            if not g_ctrl or not geo:
                print 'Intermediate Ctrl Warning: '+str(ref)+' contains illegal hierarchy or naming of global_ctrl, poly and asb, ignored.'
                self.setTransformation(g_ctrl, g_ctrl_transformation)
                self.safeDelete( ctrl )
                continue

            # scale ctrl and copy transformation
            bbox = self.getBoundingBox(g_ctrl,geo)
            try:
                s = math.sqrt( (bbox.max()[0] - bbox.min()[0])**2 + (bbox.max()[2] - bbox.min()[2])**2 )
            except:
                s = 1.0
            if s > 0:
                int_ctrl.setScale( [s,s,s] )
            else:
                print 'Warning on add_intermediate_ctrl(): width of bbox is zero'

            pm.makeIdentity(int_ctrl, apply=True)
            #self.copyTransformation( g_ctrl, int_ctrl )

            # is the scale of global_ctrl connected?
            isScaleConnected = pm.connectionInfo(g_ctrl.attr('scaleX'), id=True) or pm.connectionInfo(g_ctrl.attr('scaleY'), id=True) or pm.connectionInfo(g_ctrl.attr('scaleZ'), id=True)
            # does global_ctrl has globalScale attr?
            hasGlobalScale = g_ctrl.hasAttr('globalScale')

            # deal globalScale attr
            '''
            if isScaleConnected:
                if int_ctrl.hasAttr('globalScale') and int_root_ctrl.hasAttr('globalScale'):
                    int_ctrl.globalScale >> int_ctrl.scaleX
                    int_ctrl.globalScale >> int_ctrl.scaleY
                    int_ctrl.globalScale >> int_ctrl.scaleZ
                    int_ctrl.attr('globalScale').set( 1 )
                    int_root_ctrl.globalScale >> int_root_ctrl.scaleX
                    int_root_ctrl.globalScale >> int_root_ctrl.scaleY
                    int_root_ctrl.globalScale >> int_root_ctrl.scaleZ
                    int_root_ctrl.attr('globalScale').set( 1 )
            '''

            # constraint and connect globalScale or scaleXYZ attr
            try:
                pm.parentConstraint( int_root_ctrl, g_ctrl, maintainOffset=False )
                if hasGlobalScale:
                    # This is old version of scale
                    if isScaleConnected:
                        g_scale = g_ctrl.attr('globalScale').get()
                        int_root_ctrl.globalScale >> g_ctrl.globalScale
                        int_root_ctrl.attr('globalScale').set(g_scale)
                        self.setAttrState(int_root_ctrl, attributes=['sx', 'sy', 'sz'], lock=True, keyable=False, channelBox=False)
                    else:
                        g_scale = g_ctrl.attr('globalScale').get()
                        if g_scale == 1:
                            g_scale = g_ctrl.getScale()
                        else:
                            g_scale = [g_scale, g_scale, g_scale]
                        pm.scaleConstraint( int_root_ctrl, g_ctrl, maintainOffset=False )
                        int_root_ctrl.setScale( g_scale )
                        self.setAttrState(int_root_ctrl, attributes=['globalScale'], lock=True, keyable=False, channelBox=False)
                else:
                    if not isScaleConnected:
                        g_scale = g_ctrl.getScale()
                        pm.scaleConstraint( int_root_ctrl, g_ctrl, maintainOffset=False )
                        int_root_ctrl.setScale( g_scale )
                        self.setAttrState(int_root_ctrl, attributes=['globalScale'], lock=True, keyable=False, channelBox=False)
                    else:
                        self.setAttrState(int_root_ctrl, attributes=['sx', 'sy', 'sz', 'globalScale'], lock=True, keyable=False, channelBox=False)
            except:
                print 'Intermediate Ctrl Warning: there are connections on node '+str(g_ctrl)+', or those attributes had been keyed or locked, therefore can not be constrainted to '+str(int_root_ctrl)
                self.setTransformation(g_ctrl, g_ctrl_transformation)
                self.safeDelete( ctrl )
                #self.intermediate_ctrl = self.list_intermediate_ctrl()
                continue

            try:
                # lock and hide attr
                self.lockTransform(int_ctrl)
                int_ctrl.setAttr('globalScale', lock=True)
            except:
                pass

            try:
                # hide global_ctrl
                g_ctrl.getShape().attr('visibility').set(0)
                g_ctrl.getShape().setAttr('visibility', lock=True)
            except:
                pass

            # restore transforms of reference on int_root_ctrl after adding intermediate control
            self.setTransformation(int_root_ctrl, g_ctrl_transformation)
            # restore namespace
            pm.namespace(set=current_ns)

        self.update()
        #self.intermediate_ctrl = self.list_intermediate_ctrl()

        return True

    def delete_intermediate_ctrl(self):
        '''
        delete all intermediate_ctrl
        Note: this method should not be called independently, use delete_ctrl() which call this method and do other deletion
        '''
        int_exists = {}
        for ref in self.ref_mod+self.ref_asb:
            int_ctrl = [n for n in ref.getChildren() if 'intermediate_ctrl' in str(n)]
            if int_ctrl:
                int_root_ctrl = [r for r in int_ctrl[0].getChildren() if 'intermediate_root_ctrl' in str(r)]
                if int_root_ctrl:
                    g = self.findGlobalCtrl(ref)
                    int_exists[int_ctrl[0]] = [int_root_ctrl[0],g]

        # also delete any one exists under root world with and without namespace
        int_exists_world = []
        int_exists_world.extend( pm.ls('|*intermediate_ctrl', type='transform') )
        int_exists_world.extend( pm.ls('|*:*intermediate_ctrl', type='transform') )
        if int_exists:
            for int_ctrl in int_exists:
                try:
                    int_root_ctrl = int_exists.get(int_ctrl)[0]
                    g_ctrl = int_exists.get(int_ctrl)[1]
                    tran = self.getTransformation( int_root_ctrl, 'world' )
                    pm.delete( int_ctrl )
                    self.setTransformation(g_ctrl, tran)
                    # show global_ctrl
                    try:
                        g_ctrl.getShape().attr('visibility').set(1)
                    except:
                        print 'delete_intermediate_ctrl Warning: unable to set visibility of '+str(g_ctrl)+' to on, ignored.'
                except:
                    print traceback.format_exc()
                    print 'delete_intermediate_ctrl Warning: '+str(int_ctrl)+' can not be deleted before proceeding, ignored.'

        for i in int_exists_world:
            try:
                pm.delete(i)
            except:
                pass
        self.intermediate_ctrl = self.list_intermediate_ctrl()

    def delete_ctrl(self):
        '''
        This is the main deletion method of AssemblyOperator Class
        '''
        self.update()
        self.delete_intermediate_ctrl()
        if pm.objExists('|master|rig'):
            try:
                rig_node = pm.PyNode('|master|rig')
                pm.lockNode( rig_node, lock=False )
                pm.delete( rig_node )
            except:
                print 'delete_ctrl Error: something wrong when deleting |master|rig'

    def add_ctrl(self):
        '''
        Add global_ctrl and intermediate_ctrl for assembly, this is the main creation method of AssemblyOperator Class
        '''
        # make sure that we are in adequate pose before launching
        try:
            asb_node = pm.PyNode('|master|asb')
        except:
            print 'add_ctrl warning: can not find |master|asb group!'
            return False

        self.update()

        # delete existing rig and intermediate_ctrl
        self.delete_ctrl()

        ctrl_path = self.asb_ctrl_path + 'asb_global_control.ma'
        if not os.path.isfile(ctrl_path):
            print 'add_ctrl warning: Can not find '+ctrl_path
            return False

        # create new sets of intermediate_ctrl
        if not self.add_intermediate_ctrl():
            print 'add_ctrl warning: Errors when adding intermediate_ctrl'
            return False

        # create new rig
        ns_fn = lambda x: x if x.startswith(':') else ':'+x
        current_ns = ns_fn( pm.namespaceInfo(cur=True) )
        pm.namespace(set=':')
        l_nodes = None
        try:
            l_nodes = pm.importFile( ctrl_path, returnNewNodes=True )
        except:
            print 'Error on add_ctrl() when importing '+ctrl_path
            self.safeDelete(l_nodes)
            pm.namespace(set=current_ns)
            return False
        pm.namespace(set=current_ns)

        rig_node = l_nodes[0]
        l_ctrl_nodes = []
        l_lock_nodes = [rig_node]
        global_ctrl = None
        root_ctrl = None
        for node in l_nodes:
            if node.fullPath().endswith('zero'):
                l_lock_nodes.append(node)
            if node.fullPath().endswith('ctrl'):
                l_ctrl_nodes.append(node)
            if node.name() == ('global_ctrl'):
                global_ctrl = node
            if node.name() == ('root_ctrl'):
                root_ctrl = node

        # scale the rig node
        bbox = asb_node.boundingBox()
        #pm.move(rig_node, [(bbox.min()[0] + bbox.max()[0])/2, bbox.min()[1], (bbox.min()[2] + bbox.max()[2])/2])
        try:
            s = math.sqrt( (bbox.max()[0] - bbox.min()[0])**2 + (bbox.max()[2] - bbox.min()[2])**2 )
        except:
            s = 1.0
        pm.scale(rig_node, [s, s, s])
        pm.makeIdentity(rig_node, apply=True)
        pm.delete(rig_node, ch=True)

        # move the global_ctrl of rig node after scale and makeIdentity
        #center = [(bbox.max()[0]-bbox.min()[0])/2+bbox.min()[0], (bbox.max()[1]-bbox.min()[1])/2+bbox.min()[1], (bbox.max()[2]-bbox.min()[2])/2+bbox.min()[2]]
        #pm.move(global_ctrl, center)

        if global_ctrl and global_ctrl.hasAttr('globalScale'):
            pm.connectAttr( global_ctrl.fullPath()+".globalScale", global_ctrl.fullPath()+".scaleX", f=True)
            pm.connectAttr( global_ctrl.fullPath()+".globalScale", global_ctrl.fullPath()+".scaleY", f=True)
            pm.connectAttr( global_ctrl.fullPath()+".globalScale", global_ctrl.fullPath()+".scaleZ", f=True)

        for node in l_lock_nodes:
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                node.setAttr(attr, lock=True, keyable=False, channelBox=False )

        for node in l_ctrl_nodes:
            for attr in ['sx', 'sy', 'sz']:
                node.setAttr(attr, lock=True, keyable=False, channelBox=False )

        # parent rig_node under master
        pm.parent(rig_node, '|master')

        # connect scale of global_ctrl of rig to scale of intermediate_ctrl
        if global_ctrl:
            self.constraintScale(global_ctrl, self.intermediate_ctrl)

        # constraint translation and rotation of intermediate_ctrl to rig|root_ctrl
        if root_ctrl:
            self.constraint( root_ctrl, self.intermediate_ctrl )

        # Lock |master and |master|asb
        for node in [pm.PyNode('|master'), pm.PyNode('|master|asb')]:
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                node.setAttr(attr, lock=True, keyable=False )
        return True

    def constraint(self, root, rig_sets):
        for rig in rig_sets:
            try:
                self.unlockTransform(rig)
                pm.parentConstraint( root, rig, maintainOffset=False )
                self.lockTransform(rig)
            except:
                print 'constraint Error: unable parent constraint '+str(rig)+' to '+str(root)

    def constraintScale(self, global_ctrl, rig_sets):
        for rig in rig_sets:
            try:
                self.unlockTransform(rig)
                pm.scaleConstraint( global_ctrl, rig, maintainOffset=False )
                self.lockTransform(rig)
            except:
                print 'constraint Error: unable scale constraint '+str(rig)+' to '+str(global_ctrl)

    def safeDelete(self, obj):
        try:
            pm.delete(obj)
        except:
            pass






class AssemblyOperatorRig(AssemblyOperator):

    def add_intermediate_ctrl(self):
        '''
        add intermediate control for mod and rig asset(not asb assets) in assembly group. This is necessary for moving assembly all in one while
        keep capability of individuals' transformation.
        Note: this method should not be called independently, use add_ctrl() which call this method and do other setups
        '''
        mod_ctrl_path = self.asb_ctrl_path + 'intermediate_mod.ma'
        asb_ctrl_path = self.asb_ctrl_path + 'intermediate_asb.ma'
        if not os.path.isfile(mod_ctrl_path) or not os.path.isfile(asb_ctrl_path):
            print 'Can not find '+mod_ctrl_path
            print 'Can not find '+asb_ctrl_path
            return False

        #delete any existing intermediate ctrl under root world with and without namespace
        root_int_exists = []
        root_int_exists.extend( pm.ls('|*intermediate_ctrl', type='transform') )
        root_int_exists.extend( pm.ls('|*:*intermediate_ctrl', type='transform') )
        for rie in root_int_exists:
            try:
                pm.lockNode(rie, lock=False)
                pm.delete(rie)
            except:
                print 'Intermediate Ctrl Warning: '+str(rie)+' can not be deleted before proceeding, ignored.'

        for ref in self.ref_mod + self.ref_asb:
            # here we assume there are rig, poly or asb group under every master transform
            # delete ctrl if it exists, then create new one

            ref_string = str(ref)

            int_exists = [n for n in ref.getChildren() if 'intermediate_ctrl' in str(n)]
            if int_exists:
                for i in int_exists:
                    try:
                        pm.lockNode( i, lock=False)
                        pm.delete( i )
                    except:
                        print 'Intermediate Ctrl Warning: '+str(i)+' can not be deleted before proceeding, ignored.'
                        #self.intermediate_ctrl = self.list_intermediate_ctrl()
                        continue

            # create intermediate controls
            ns_fn = lambda x: x if x.startswith(':') else ':'+x
            ns = ns_fn( pm.referenceQuery( ref, namespace=True ) )
            current_ns = ns_fn( pm.namespaceInfo(cur=True) )
            # set namespace, so everything newly created is under this namespace
            pm.namespace(set=ns)
            ctrl = None
            try:
                if ref in self.ref_mod:
                    ctrl = pm.importFile( mod_ctrl_path, returnNewNodes=True )
                else:
                    ctrl = pm.importFile( asb_ctrl_path, returnNewNodes=True )
            except:
                print 'Error on add_intermediate_ctrl() when import intermediate_*.ma file'
                self.safeDelete(ctrl)
                continue
            #pm.namespace(set=current_ns)

            # grab global_ctrl, root_ctrl and bbox of poly group
            g_ctrl = self.findGlobalCtrl( ref )
            g_ctrl_string = str(g_ctrl)
            geo = self.findPoly( ref ) if ref in self.ref_mod else self.findAsb( ref )
            geo_string = str(geo)

            ### store transformation of global_ctrl
            g_ctrl_transformation = self.getTransformation(g_ctrl)

            # parent intermediate control under ref
            try:
                pm.parent(ctrl[0], ref)
            except:
                print 'Error on add_intermediate_ctrl() when trying to parent '+str(ctrl[0])+' under '+str(ref)
                self.safeDelete(ctrl)
                continue
            int_ctrl = ctrl[0]
            int_root_ctrl = ctrl[2]

            if not g_ctrl or not geo:
                print 'Intermediate Ctrl Warning: '+str(ref)+' contains illegal hierarchy or naming of global_ctrl, poly and asb, ignored.'
                self.safeDelete( ctrl )
                continue

            # scale ctrl and copy transformation
            bbox = self.getBoundingBox(g_ctrl,geo)
            try:
                s = math.sqrt( (bbox.max()[0] - bbox.min()[0])**2 + (bbox.max()[2] - bbox.min()[2])**2 )
            except:
                s = 1.0
            if s > 0:
                int_ctrl.setScale( [s,s,s] )
            else:
                print 'Warning on add_intermediate_ctrl(): width of bbox is zero'

            pm.makeIdentity(int_ctrl, apply=True)
            #self.copyTransformation( g_ctrl, int_ctrl )

            try:
                # lock and hide attr
                self.lockTransform(int_ctrl)
                self.lockTransform(int_root_ctrl)
                int_ctrl.attr('lodVisibility').set(False)
            except:
                pass

            self.setTransformation(int_root_ctrl, g_ctrl_transformation)

            # restore namespace
            pm.namespace(set=current_ns)

        self.update()
        #self.intermediate_ctrl = self.list_intermediate_ctrl()

        return True


    def delete_intermediate_ctrl(self):
        '''
        delete all intermediate_ctrl
        Note: this method should not be called independently, use delete_ctrl() which call this method and do other deletion
        '''
        int_exists = {}
        for ref in self.ref_mod+self.ref_asb:
            int_ctrl = [n for n in ref.getChildren() if 'intermediate_ctrl' in str(n)]
            if int_ctrl:
                int_root_ctrl = [r for r in int_ctrl[0].getChildren() if 'intermediate_root_ctrl' in str(r)]
                if int_root_ctrl:
                    g = self.findGlobalCtrl(ref)
                    int_exists[int_ctrl[0]] = [int_root_ctrl[0],g]

        # also delete any one exists under root world with and without namespace
        int_exists_world = []
        int_exists_world.extend( pm.ls('|*intermediate_ctrl', type='transform') )
        int_exists_world.extend( pm.ls('|*:*intermediate_ctrl', type='transform') )
        if int_exists:
            for int_ctrl in int_exists:
                try:
                    int_root_ctrl = int_exists.get(int_ctrl)[0]
                    pm.delete( int_ctrl )
                except:
                    print traceback.format_exc()
                    print 'delete_intermediate_ctrl Warning: '+str(int_ctrl)+' can not be deleted before proceeding, ignored.'

        for i in int_exists_world:
            try:
                pm.delete(i)
            except:
                pass
        self.intermediate_ctrl = self.list_intermediate_ctrl()