import os as os
import maya.cmds as cmds
import production.pipeline.lcProdProj as lcp
reload(lcp)

try:
    import maya.cmds as cmds
    if '2013' in cmds.about(v=True): 
        import xml.etree.ElementTree as ET
    else:
        from lxml import etree as ET
except:
    try:
        from lxml import etree as ET
    except:
        import xml.etree.ElementTree as ET
        
def add_texture_map(shader_node, map_path):
    file_n = cmds.shadingNode('file', asTexture=True)
    cmds.setAttr(file_n + '.fileTextureName', map_path, type='string')
    uv_n = cmds.shadingNode('place2dTexture', asUtility=True) 
    cmds.connectAttr(uv_n + '.coverage', file_n + '.coverage', f = True)
    cmds.connectAttr(uv_n + '.translateFrame', file_n + '.translateFrame', f = True)
    cmds.connectAttr(uv_n + '.rotateFrame', file_n + '.rotateFrame', f = True)
    cmds.connectAttr(uv_n + '.mirrorU', file_n + '.mirrorU', f = True)
    cmds.connectAttr(uv_n + '.mirrorV', file_n + '.mirrorV', f = True)
    cmds.connectAttr(uv_n + '.stagger', file_n + '.stagger', f = True)
    cmds.connectAttr(uv_n + '.wrapU', file_n + '.wrapU', f = True)
    cmds.connectAttr(uv_n + '.wrapV', file_n + '.wrapV', f = True)
    cmds.connectAttr(uv_n + '.repeatUV', file_n + '.repeatUV', f = True)
    cmds.connectAttr(uv_n + '.offset', file_n + '.offset', f = True)
    cmds.connectAttr(uv_n + '.rotateUV', file_n + '.rotateUV', f = True)
    cmds.connectAttr(uv_n + '.noiseUV', file_n + '.noiseUV', f = True)
    cmds.connectAttr(uv_n + '.vertexUvOne', file_n + '.vertexUvOne', f = True)
    cmds.connectAttr(uv_n + '.vertexUvTwo', file_n + '.vertexUvTwo', f = True)
    cmds.connectAttr(uv_n + '.vertexUvThree', file_n + '.vertexUvThree', f = True)
    cmds.connectAttr(uv_n + '.vertexCameraOne', file_n + '.vertexCameraOne', f = True)
    cmds.connectAttr(uv_n + '.outUV', file_n + '.uv', f = True)
    cmds.connectAttr(uv_n + '.outUvFilterSize', file_n + '.uvFilterSize', f = True)
    cmds.connectAttr( file_n + '.outColor', shader_node + '.color', f = True)

# def get_low_tex_xml_info(xml_file):
#     """
#     get mat info xml data in srf
#     """
#     try:
#         tree = ET.parse(xml_file)
#     except Exception, e:
#         raise Exception("Error: cannot parse file: " + xml_file)

#     result = {'map':[],'color':[]}
#     root = tree.getroot()
#     inst_list = root.getiterator('difMap')
#     for ist in inst_list:
#         tx_path=ist.attrib.get('path')
#         if tx_path:
#             temp_map={}
#             temp_map[tx_path]=[]
#             shape_list=ist.getiterator('shape')
#             for sl in shape_list:
#                 if sl.attrib.get('path'):
#                    temp_map[tx_path].append(sl.attrib.get('path'))
        	
#             result['map'].append(temp_map)

#     inst_list = root.getiterator('difCo')
#     for ist in inst_list:
#         col_value=ist.attrib.get('value')
#         if col_value:
#             temp_map={}
#             temp_map[col_value]=[]
#             shape_list=ist.getiterator('shape')
#             for sl in shape_list:
#                 if sl.attrib.get('path'):
#                    temp_map[col_value].append(sl.attrib.get('path'))
                    
#             result['color'].append(temp_map)

#     return result

def name_convert(objects):
    objs = []
    for obj in objects:
        obj = '/master' + obj.split('master')[1]
        obj = obj.replace('/geometry', '')
        obj = obj.replace('/', '|')
        objs.append(obj)
    return objs

def assign_shader(objects, shading_grp):
    for obj in objects:
        if cmds.objExists(obj):
            cmds.sets(obj,fe=shading_grp)

def create_shader(version_path):
    newLambert = cmds.shadingNode('lambert', asShader=True)
    newShdGrp = cmds.sets(name=newLambert + 'SG', renderable=True, noSurfaceShader=True, empty=True )
    cmds.connectAttr(newLambert + '.outColor', newShdGrp + '.surfaceShader', f=True)
    cmds.addAttr(newLambert, ln='version', dt='string')
    cmds.setAttr(newLambert+'.version', version_path, type='string')
    return newLambert, newShdGrp

def apply(xml_path,pass_name='default'):
    ver_path = '/'.join(xml_path.split('/')[:-2])
    tex_path = xml_path.split('/publish/')[0] + '/publish/tex_low/'
    list_info = lcp.lcProdProj.get_low_tex_xml_info2(xml_path)
    #get default pass data,from yingjie
    list_info=list_info.get(pass_name)
    
    color_shader_list = []
    map_shader_list = []
    color_list = list_info['color']
    for i in color_list:
        for j in i:
            rgbw = j.split(',')
            red = float(rgbw[0])
            green = float(rgbw[1])
            blue = float(rgbw[2])
            trasparent = float(rgbw[3])
            # Create new shader
            myLambert, myShdGrp= create_shader(ver_path)
            color_shader_list.append(myLambert)
            cmds.setAttr(myLambert + '.color', red, green, blue, type='double3')
            cmds.setAttr(myLambert + '.transparency', trasparent, trasparent, trasparent, type='double3')
            objs = i[j]
            objs = name_convert(objs)
            assign_shader(objs, myShdGrp)

    map_list = list_info['map']
    for i in map_list:
        for j in i:
            map_file = tex_path + os.path.splitext(j)[0] + '.jpg'
            if '<udim>' in j:
                # Assign shader by UV region
                objs = i[j]
                objs = name_convert(objs)
                uv_region = {}

                for obj in objs:
                    if cmds.objExists(obj):
                        for n in range(cmds.polyEvaluate(obj, uv=True)):
                            uv_x = int(cmds.polyEditUV(obj + '.map[' + str(n) + ']', q=True)[0]) + 1
                            uv_y = int(cmds.polyEditUV(obj + '.map[' + str(n) + ']', q=True)[1]) * 10
                            uv_xy = uv_x + uv_y
                            
                            if not uv_region.has_key(uv_xy):
                                uv_region[uv_xy] = [obj + '.map[' + str(n) + ']']
                            else:
                                uv_region[uv_xy].append(obj + '.map[' + str(n) + ']')

                for r in uv_region:
                    myLambert, myShdGrp= create_shader(ver_path)
                    map_shader_list.append(myLambert)
                    add_texture_map(myLambert, map_file.replace('<udim>', '10'+str(r).zfill(2)))

                    uv_region[r] = cmds.polyListComponentConversion(uv_region[r], toFace=True)

                    for j in uv_region[r]:
                        cmds.sets(j,fe=myShdGrp)
            else:
                # Assign shader by object
                myLambert, myShdGrp= create_shader(ver_path)
                map_shader_list.append(myLambert)
                add_texture_map(myLambert, map_file)
                objs = i[j]
                objs = name_convert(objs)
                assign_shader(objs, myShdGrp)
    
    shader_grps = cmds.ls(type='shadingEngine')
    for sh in shader_grps:
        if not cmds.listConnections(sh, type='mesh'):
            # Not connect to any poly mesh
            try:
                cmds.delete(sh)
            except:
                print 'Cannot delete',sh

    shaders_all = cmds.ls(mat=True)
    for sh in shaders_all:
        if not cmds.listConnections(sh, type='shadingEngine'):
            # No shading group
            try:
                cmds.delete(sh)
            except:
                print 'Cannot delete',sh

    for sh in color_shader_list:
        if cmds.objExists(sh):
            cmds.rename(sh, 'surface_' + ver_path.split('.')[-1] + '_rgbColor1')
    
    for sh in map_shader_list:
        if cmds.objExists(sh):
            cmds.rename(sh, 'surface_' + ver_path.split('.')[-1] + '_textureMap1')
