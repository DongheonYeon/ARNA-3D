import bpy
import os

# === 1) 불러올 OBJ 파일 경로 ===
PATH = r"C:\Users\USER\Documents\vscode_projects\ARNA-3D\obj_A (2).glb"  # <- 여기에 경로 입력
# --- 1) 파일 임포트: 확장자에 맞는 오퍼레이터 사용 ---
ext = os.path.splitext(PATH)[1].lower()

# 임포트 전에 선택 해제
bpy.ops.object.select_all(action='DESELECT')

if ext == ".obj":
    # Blender 4.x: wm.obj_import, 2.8~3.x: import_scene.obj (둘 다 시도)
    try:
        bpy.ops.wm.obj_import(filepath=PATH)
    except Exception:
        bpy.ops.import_scene.obj(filepath=PATH)
elif ext in (".glb", ".gltf"):
    # glTF 임포터(Add-on: io_scene_gltf2)
    bpy.ops.import_scene.gltf(filepath=PATH)
else:
    raise ValueError(f"지원하지 않는 확장자: {ext}")

# --- 2) 타겟 선택 규칙 정의 ---
KEYS = ("kidney", "fat")

def is_target_mesh(obj: bpy.types.Object) -> bool:
    if obj.type != 'MESH':
        return False
    name_ok = any(k in obj.name.lower() for k in KEYS)
    data_ok = obj.data and any(k in obj.data.name.lower() for k in KEYS)
    return name_ok or data_ok

# glTF는 빈(EMPTY) 부모 밑에 Mesh가 달리는 경우가 많음 → 씬 전체에서 탐색
targets = [o for o in bpy.data.objects if is_target_mesh(o)]

print(f"[INFO] Found target meshes: {[o.name for o in targets]}")

if not targets:
    print("[WARN] 'Kidney' 또는 'Fat'가 이름에 포함된 Mesh 오브젝트를 찾지 못했습니다.")
else:
    # --- 3) 각 타겟에 대해 Recalculate Outside 수행 ---
    for obj in targets:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Edit 모드 진입
        if bpy.context.object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        # 전체 선택 후 노멀 일관화(Outside)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)

        # Object 모드 복귀
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"[OK] Recalculated Outside: {obj.name}")

    print("[DONE] normals_make_consistent(inside=False) 완료.")
    
bpy.ops.export_scene.gltf(
filepath=r"C:\Users\USER\Documents\vscode_projects\ARNA-3D\obj_A(2)export.glb",
export_format='GLB',    # 'GLTF_SEPARATE', 'GLTF_EMBEDDED'도 가능
use_selection=False     # True로 하면 선택한 오브젝트만
)