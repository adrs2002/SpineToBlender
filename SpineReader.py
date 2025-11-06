import bpy
import os
import json

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

from pathlib import Path

armature_BaseName = 'アーマチュア'
# armature_BaseName = 'Armature'


text_block = bpy.data.texts.new("PrintResult")



class J_SpineImageReader(Operator, ImportHelper):

    bl_idname = "test.open_filebrowser"
    bl_label = "Open the file browser (yay)"
    
    filter_glob: StringProperty(
        default='*.json;*.json;',
        options={'HIDDEN'}
    )
    
    some_boolean: BoolProperty(
        name='Do a thing',
        description='Do a thing with the file you\'ve selected',
        default=True,
    )

    def execute(self, context):
        """Do something with the selected file(s)."""
        addz = 0
        with open(self.filepath, 'r') as fp:
            file_data = json.load(fp)
    
            imageBasePath = file_data['skeleton']['images']
            if len(imageBasePath) == 0:
                imageBasePath = self.filepath
                imageBasePath = imageBasePath[0:imageBasePath.rfind("\\")]

            text_block.write(imageBasePath)
            text_block.write('\n')
            
            
            ArmatureObj = bpy.data.objects.get(armature_BaseName)
            if ArmatureObj is None:
                # bpy.ops.object.armature_add(scale=(1,1,1), enter_editmode=True, align="WORLD", location=(0,0,0))
                # ArmatureObj = bpy.data.objects.get(armature_BaseName)
                ArmatureObj = bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=(0,0,0))
                # ArmatureObj.name = armature_BaseName
                bpy.ops.object.mode_set(mode='OBJECT')               
            
            
            
            for skin_val in file_data['skins']['default']:
                text_block.write(skin_val)
                text_block.write('\n')
                
                for s_val in file_data['skins']['default'][skin_val].values():
                
                    # メッシュ作成
                    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(s_val['x'] * 0.01, s_val['y'] * 0.01, addz), scale=(1, 1, 1))
                    bpy.ops.transform.resize(value=(s_val['width'] * 0.01, s_val['height'] * 0.01, 1.0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
 
                    # マテリアルを作成し、テクスチャをセットする
                    for obj in bpy.context.selected_objects:
                        obj.name = skin_val                        
                        new_material_textureset(skin_val, imageBasePath, skin_val)
                    
                    
                    # ボーンを作成する
                    if skin_val[0:2] == "MB":
  
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.context.view_layer.objects.active = None
                        bpy.context.view_layer.objects.active  = bpy.data.objects.get(armature_BaseName)                        
                        # bpy.ops.object.mode_set(mode='OBJECT')            
                        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                        b =  bpy.data.objects.get(armature_BaseName).data.edit_bones.new(skin_val)                        
                        b.head = (s_val['x'] * 0.01,  s_val['y'] * 0.01 - s_val['height'] * 0.005, 0)
                        b.tail = (s_val['x'] * 0.01,  s_val['y'] * 0.01 + s_val['height'] * 0.005, 0)                        
                        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                   
                        # ウェイト割当
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.context.view_layer.objects.active = None
                        bpy.context.view_layer.objects.active = bpy.data.objects.get(skin_val)
                        bpy.context.object.vertex_groups.new(name=skin_val)
                        targetMod = bpy.context.object.modifiers.new(type='ARMATURE', name=armature_BaseName)
                        targetMod.object = bpy.data.objects[armature_BaseName]
                        
                        bpy.context.object.vertex_groups.active_index=bpy.context.object.vertex_groups[skin_val].index        
                        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                        # 全頂点を選択状態にする
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.context.scene.tool_settings.vertex_group_weight=1.0
                        bpy.ops.object.vertex_group_assign()
                        
                        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                        
                        
                    addz += 0.1
                    break;
        
        return {'FINISHED'}

#######################################

def register():
    bpy.utils.register_class(J_SpineImageReader)


def unregister():
    bpy.utils.unregister_class(J_SpineImageReader)


def new_material_textureset(arg_objectname,arg_applyfilepath,arg_applyfilename):
      
  # 指定オブジェクトを取得する
  # selectob = bpy.context.scene.objects[arg_objectname]
  # 変更オブジェクトをアクティブに変更する
  # bpy.context.scene.objects.active=selectob

  # 新規マテリアルを作成する
  new_material=bpy.data.materials.new(arg_applyfilename)
  # マテリアルスロットを追加する
  bpy.ops.object.material_slot_add()
  # 作成したマテリアルスロットに新規マテリアルを設定する
  bpy.context.object.active_material=new_material

  # 新規テクスチャを作成する
  new_texture=bpy.data.textures.new(arg_applyfilename,type='IMAGE')
  # マテリアルにテクスチャスロットを追加する
  # new_texture_slot=new_material.texture_slots.add()
  # 作成したテクスチャスロットに新規テクスチャを設定する
  # new_texture_slot.texture=new_texture
  
  # テクスチャ画像のファイルパスを取得する
  allpy_filepath=arg_applyfilepath + "\\" + arg_applyfilename + '.png'
 
  # 反映画像を読み込み
  # apply_image=bpy.data.images.load(filepath=allpy_filepath)
  # 作成した新規テクスチャに画像を設定する
  # new_texture.image=apply_image

  text_block.write(allpy_filepath)
  text_block.write('\n')
    
  new_material.use_nodes = True
  bsdf = new_material.node_tree.nodes["プリンシプルBSDF"]
  texImage = new_material.node_tree.nodes.new('ShaderNodeTexImage')
  texImage.image = bpy.data.images.load(allpy_filepath)
  new_material.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
  new_material.blend_method = 'BLEND'
  # new_material.shadow_method = 'CLIP'
  new_material.node_tree.links.new(bsdf.inputs['Alpha'], texImage.outputs['Alpha'])
  
  return


def addBone(arg_objectname, head_x, head_y, tail_x, tail_y):

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = None

    bpy.context.view_layer.objects.active  = bpy.data.objects.get(armature_BaseName)
    # bpy.ops.object.mode_set(mode='OBJECT')            
    bpy.ops.object.mode_set(mode='EDIT')
    b =  bpy.data.objects.get(armature_BaseName).data.edit_bones.new(arg_objectname)
    b.head = (head_x, head_y ,0)
    b.tail = (tail_x, tail_y, 0)
    bpy.ops.object.mode_set(mode='OBJECT')

    return



if __name__ == "__main__":
    register()

    # test call
    bpy.ops.test.open_filebrowser('INVOKE_DEFAULT')
