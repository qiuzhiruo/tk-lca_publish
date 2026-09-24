# -*- coding:utf-8 -*-

import os
import math
import pymel.core as pm

import sys
sys.path.append( '/'.join(os.path.dirname(__file__).replace('\\','/').split('/')[:-1]) + '/gen' )
import assembly_operator as asop

class ScnAssemblyOperator( asop.AssemblyOperator ):
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

            # this is override part
            if '/rig/' in str(file_ref.path):
                # rig asset's edits shouldn't be deleted on scn publish
                delete_ref_bool = False
            # we don't delete edits on scn publish
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