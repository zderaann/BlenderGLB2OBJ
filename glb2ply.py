bl_info = {
    "name": "Glb files to Obj",
    "author": "AZ",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "warning": "",
    "wiki_url": "",
}

import bpy
import sys
import os
from shutil import copyfile

# params: path_to_glb_folder
# 


def register():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]
    print('args parsed')

    # Delete any startup objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete() 
    print('deleted startup objects')

    # Load model
    print('walking folder')
    folder_path = argv[0]
    if not folder_path.endswith('/'):
        folder_path = folder_path + '/'
    for r, d, f in os.walk(folder_path):
        for file in f:
            if file.endswith('.glb'):
                print('Found GLB file')
                bpy.ops.import_scene.gltf(filepath= r + file)

                # Parse filename
                filename = (file.split('.'))[0]                

                # Switch to OBJECT mode
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='SELECT')
                for im in bpy.data.images:
                    if im.name != 'Render Result' and im.name != 'Viewer Node':
                        print('Saving image ' + im.name)
                        im.save()

                for ob in bpy.context.selected_editable_objects:
                    material_slots = ob.material_slots

                    for m in material_slots:
                        material = m.material
                        material.use_nodes = True
                        BSDFnode = material.node_tree.nodes.get('Principled BSDF')
                        BSDFoutput = BSDFnode.outputs.get('BSDF')
                        outputnode = material.node_tree.nodes.get('Material Output')
                        outputnodeinput = outputnode.inputs.get('Surface')
                        material.node_tree.links.new(BSDFoutput, outputnodeinput)

                        

                # Export as OBJ
                target_file = r + filename + '.obj'

                bpy.ops.export_scene.obj(filepath=target_file)

                with open(r + filename + '.mtl', 'r') as mat_file:
                    txt = ''
                    for line in mat_file:
                        if 'map_Kd' in line:
                            parsed = line.split(' ')
                            img_name = parsed[1].split('\\')[-1]
                            img_name = img_name[0:-1]
                            copyfile(parsed[1][0:-1], folder_path + img_name + '.jpg')
                            txt = txt + parsed[0] + ' ' + img_name + '.jpg'
                            pass
                        else:
                            txt = txt + line

                out_mat = open(r + filename + '.mtl', 'w')
                out_mat.write(txt)
                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.delete() 


                

def unregister():
    pass


if __name__ == "__main__":
    register()