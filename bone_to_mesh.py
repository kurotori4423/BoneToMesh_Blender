# 参考にさせていただいたコード
# ボーンからメッシュ形状を作成するアドオン - Blenderとかとか
# http://yukimi-blend.blogspot.com/2017/07/blog-post.html

bl_info = {
    "name": "activebone to mesh",
    "description": "選択されたボーンから、ローカル軸でマテリアル分けされたメッシュを作成　参考：http://yukimi-blend.blogspot.com/2017/07/blog-post.html",
    "author": "Kurotori",
    "version": (0,1),
    "blender": (2, 7, 9),
    "location": "Object",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"}
import bpy
import math
from mathutils import Vector, Matrix
class active_bone_to_mesh(bpy.types.Operator):
    bl_idname = "object.active_bone_to_mesh"
    bl_label = "選択ボーンからメッシュ"
    bl_description = "選択したボーンのエンベロープを元にカプセル形状を作成"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if context.mode == 'EDIT_ARMATURE':
            obj = context.active_object
            #グローバル座標への変換マトリクス
            matrix_world = obj.matrix_world
            #エディットモードの状態で情報を更新
            obj.update_from_editmode()
            bones = obj.data.bones

            #追加処理 マテリアル適用
            mat_Default = bpy.data.materials.new('Default')
            mat_Default.diffuse_intensity = 1.0
            mat_Default.diffuse_color = (1.0, 1.0, 1.0)
            
            mat_X_Red = bpy.data.materials.new('X_Red')
            mat_X_Red.diffuse_intensity = 1.0
            mat_X_Red.diffuse_color = (1.0, 0.0, 0.0)
            
            mat_Z_Blue = bpy.data.materials.new('Z_Blue')
            mat_Z_Blue.diffuse_intensity = 1.0
            mat_Z_Blue.diffuse_color = (0.0, 0.0, 1.0)
            
            

            for b in bones:
                if b.select:
                    head_radius = b.head_radius
                    tail_radius = b.tail_radius
                    distance = (b.tail_local -b.head_local).length
                    mat = matrix_world*b.matrix_local
                    (vertices,faces) = get_cupsule_base2(distance)
                    #座標の変換
                    vertices = [mat*Vector(v) for v in vertices]
                    name = b.name
                    #メッシュの作成
                    mesh_obj = add_mesh_from_data(name,vertices,faces)

                    
                    mesh_obj.data.materials.append(mat_Default)
                    mesh_obj.data.materials.append(mat_Z_Blue)
                    mesh_obj.data.materials.append(mat_X_Red)
                    

                    mesh_obj.data.polygons[0].material_index = 1
                    mesh_obj.data.polygons[1].material_index = 1
                    mesh_obj.data.polygons[2].material_index = 2
                    mesh_obj.data.polygons[3].material_index = 2

                    

                    #作成元のボーンのウエイトを付加
                    v_group = mesh_obj.vertex_groups.new(name)
                    v_index = list( range( len(vertices) ) )
                    v_group.add(v_index, 1.0, 'REPLACE')
                    #モデファイアの付加
                    mesh_obj.modifiers.new("Armature", 'ARMATURE')
                    mesh_obj.modifiers["Armature"].object = obj
        return {'RUNNING_MODAL'}
#選択したボーンからカプセル形状を作成

def get_cupsule_base2(distance):
    fatY = distance/5.0
    fatXZ = distance/10.0
    pos_list = [
        (.0,.0,.0),
        (-fatXZ, distance/4., fatXZ),
        (fatXZ, distance/4., fatXZ),
        (fatXZ, distance/4., -fatXZ),
        (-fatXZ, distance/4., -fatXZ),
        (.0, distance, .0)
    ]

    face_list = [
        (0,2,1),
        (1,2,5),
        (0,3,2),
        (2,3,5),
        (0,4,3),
        (3,4,5),
        (0,1,4),
        (4,1,5)
    ]
    return(pos_list, face_list)

#データからメッシュを作成
def add_mesh_from_data(name,vertices,faces):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.objects.link(obj)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    return( obj )
 
################################################
#メニュー項目の設定
def menu_funk(self, context):
    self.layout.operator("object.active_bone_to_mesh")
 # アドオン有効化時の処理
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_edit_armature_add.append(menu_funk)
# アドオン無効化時の処理
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_edit_armature_add.remove(menu_funk)
################################################