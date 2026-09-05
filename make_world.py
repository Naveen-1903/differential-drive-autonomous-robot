#!/usr/bin/env python3
"""
Photorealistic Industrial Warehouse World Generator for Gazebo Classic 11.
Combines:
  - High-resolution industrial concrete floor with expansion joints and gloss.
  - OSHA-compliant yellow & black 45-degree hazard stripe aisle boundaries.
  - AWS RoboMaker Small Warehouse multi-tier industrial pallet racks (PBR textures).
  - OSRF Euro-pallets, textured cardboard shipping boxes, utility carts, barrels.
  - 3D warehouse workers (person_standing).
  - Industrial corrugated metal walls, roll-up overhead dock doors, safety bollards.
  - Overhead steel roof trusses, high-bay LED daylight illumination, and AGV docking pad.
"""
import os

W_LEN = 88.0    # Warehouse length along X (-44 to +44)
W_WID = 30.0    # Warehouse width along Y (-15 to +15)
W_HGT = 6.0     # Wall height
WALL_T = 0.35   # Wall thickness

def mat_custom(name):
    return f"""<material>
          <script>
            <uri>model://warehouse_assets/materials/scripts</uri>
            <uri>model://warehouse_assets/materials/textures</uri>
            <name>{name}</name>
          </script>
        </material>"""

def mat_gazebo(name):
    return f"""<material>
          <script>
            <uri>file://media/materials/scripts/gazebo.material</uri>
            <name>{name}</name>
          </script>
        </material>"""

def mat_color(r, g, b, a=1.0, spec=0.2):
    return f"""<material>
          <ambient>{r} {g} {b} {a}</ambient>
          <diffuse>{r} {g} {b} {a}</diffuse>
          <specular>{spec} {spec} {spec} 1</specular>
        </material>"""

def box_model(name, x, y, z, sx, sy, sz, mat_xml, col=True):
    col_xml = f"""<collision name="c">
        <geometry><box><size>{sx} {sy} {sz}</size></box></geometry>
      </collision>""" if col else ""
    return f"""<model name="{name}">
    <static>true</static>
    <pose>{x} {y} {z} 0 0 0</pose>
    <link name="link">
      {col_xml}
      <visual name="v">
        <geometry><box><size>{sx} {sy} {sz}</size></box></geometry>
        {mat_xml}
      </visual>
    </link>
  </model>"""

def bollard(name, x, y):
    # Safety yellow bollard with black top cap
    yellow_mat = mat_color(0.95, 0.75, 0.05, spec=0.4)
    black_mat = mat_color(0.12, 0.12, 0.12, spec=0.2)
    return f"""<model name="{name}">
    <static>true</static>
    <pose>{x} {y} 0 0 0 0</pose>
    <link name="link">
      <collision name="c">
        <pose>0 0 0.5 0 0 0</pose>
        <geometry><cylinder><radius>0.12</radius><length>1.0</length></cylinder></geometry>
      </collision>
      <visual name="post">
        <pose>0 0 0.48 0 0 0</pose>
        <geometry><cylinder><radius>0.12</radius><length>0.96</length></cylinder></geometry>
        {yellow_mat}
      </visual>
      <visual name="cap">
        <pose>0 0 0.98 0 0 0</pose>
        <geometry><cylinder><radius>0.125</radius><length>0.06</length></cylinder></geometry>
        {black_mat}
      </visual>
    </link>
  </model>"""

def roof_truss(name, x):
    # Industrial overhead steel cross-truss
    steel_mat = mat_color(0.35, 0.38, 0.42, spec=0.5)
    return f"""<model name="{name}">
    <static>true</static>
    <pose>{x} 0 5.4 0 0 0</pose>
    <link name="link">
      <visual name="top_chord">
        <pose>0 0 0.4 0 0 0</pose>
        <geometry><box><size>0.25 {W_WID} 0.15</size></box></geometry>
        {steel_mat}
      </visual>
      <visual name="bottom_chord">
        <pose>0 0 -0.4 0 0 0</pose>
        <geometry><box><size>0.25 {W_WID} 0.15</size></box></geometry>
        {steel_mat}
      </visual>
      <visual name="strut_c">
        <pose>0 0 0 0 0 0</pose>
        <geometry><box><size>0.15 0.15 0.8</size></box></geometry>
        {steel_mat}
      </visual>
      <visual name="strut_l1">
        <pose>0 6.0 0 0 0 0</pose>
        <geometry><box><size>0.15 0.15 0.8</size></box></geometry>
        {steel_mat}
      </visual>
      <visual name="strut_r1">
        <pose>0 -6.0 0 0 0 0</pose>
        <geometry><box><size>0.15 0.15 0.8</size></box></geometry>
        {steel_mat}
      </visual>
      <visual name="strut_l2">
        <pose>0 12.0 0 0 0 0</pose>
        <geometry><box><size>0.15 0.15 0.8</size></box></geometry>
        {steel_mat}
      </visual>
      <visual name="strut_r2">
        <pose>0 -12.0 0 0 0 0</pose>
        <geometry><box><size>0.15 0.15 0.8</size></box></geometry>
        {steel_mat}
      </visual>
    </link>
  </model>"""

def include_model(name, uri, x, y, z=0.0, yaw=0.0):
    return f"""<include>
    <name>{name}</name>
    <uri>{uri}</uri>
    <pose>{x} {y} {z} 0 0 {yaw}</pose>
  </include>"""

elements = []

# ==========================================
# 1. FLOOR & OSHA SAFETY BOUNDARY MARKINGS
# ==========================================
# High-resolution polished concrete warehouse floor
elements.append(box_model("floor", 0, 0, -0.05, W_LEN, W_WID, 0.1, mat_custom("Warehouse/ConcreteFloor"), col=False))

# Yellow/Black hazard stripe boundaries along the main AGV aisle (|y| = 2.5)
elements.append(box_model("hazard_line_left", 0, 2.5, 0.015, 78.0, 0.22, 0.02, mat_custom("Warehouse/HazardStripes"), col=False))
elements.append(box_model("hazard_line_right", 0, -2.5, 0.015, 78.0, 0.22, 0.02, mat_custom("Warehouse/HazardStripes"), col=False))

# Pedestrian zebra crosswalk at junction (x = 0)
for yy in [-2.0, -1.2, -0.4, 0.4, 1.2, 2.0]:
    elements.append(box_model(f"crosswalk_{yy:.1f}".replace("-","m").replace(".","_"), 0, yy, 0.018, 1.2, 0.4, 0.02, mat_color(0.95, 0.95, 0.95), col=False))

# Staging bay floor boundary lines (yellow paint)
yellow_line_mat = mat_color(0.95, 0.78, 0.05)
for sx in [-32, -24, -16, 8, 16, 24, 32]:
    elements.append(box_model(f"staging_line_L_{sx}".replace("-","m"), sx, 3.8, 0.012, 0.15, 2.4, 0.02, yellow_line_mat, col=False))
    elements.append(box_model(f"staging_line_R_{sx}".replace("-","m"), sx, -3.8, 0.012, 0.15, 2.4, 0.02, yellow_line_mat, col=False))

# ==========================================
# 2. PERIMETER WALLS & LOADING DOCKS
# ==========================================
HX = W_LEN / 2.0
HY = W_WID / 2.0
wall_mat = mat_custom("Warehouse/CorrugatedWall")

# Long East and West walls
elements.append(box_model("wall_north_side", 0, HY, W_HGT/2.0, W_LEN, WALL_T, W_HGT, wall_mat))
elements.append(box_model("wall_south_side", 0, -HY, W_HGT/2.0, W_LEN, WALL_T, W_HGT, wall_mat))

# South wall (spawn end x = -44)
elements.append(box_model("wall_spawn_end", -HX, 0, W_HGT/2.0, WALL_T, W_WID, W_HGT, wall_mat))
# Safety signs on spawn-end wall
elements.append(box_model("safety_sign_1", -HX + 0.22, 3.0, 2.4, 0.04, 2.0, 1.0, mat_custom("Warehouse/SafetySign"), col=False))
elements.append(box_model("safety_sign_2", -HX + 0.22, -3.0, 2.4, 0.04, 2.0, 1.0, mat_custom("Warehouse/SafetySign"), col=False))

# North wall (goal end x = +44) with 4 realistic loading dock doors
elements.append(box_model("wall_dock_end", HX, 0, W_HGT/2.0, WALL_T, W_WID, W_HGT, wall_mat))
dock_mat = mat_custom("Warehouse/DockDoor")
for i, dy in enumerate([-9.0, -3.0, 3.0, 9.0]):
    elements.append(box_model(f"dock_door_{i}", HX - 0.2, dy, 2.0, 0.06, 4.2, 3.8, dock_mat, col=False))

# ==========================================
# 3. OVERHEAD TRUSSES & LIGHTING
# ==========================================
for tx in [-36, -24, -12, 0, 12, 24, 36]:
    elements.append(roof_truss(f"truss_{tx}".replace("-","m"), tx))

# High-bay industrial daylight illumination fixtures (visual)
light_fixture_mat = mat_color(0.9, 0.9, 0.85, spec=0.8)
for lx in [-30, -18, -6, 6, 18, 30]:
    elements.append(box_model(f"ufo_light_{lx}".replace("-","m"), lx, 0, 5.0, 0.8, 0.8, 0.15, light_fixture_mat, col=False))

# ==========================================
# 4. AWS ROBOMAKER PALLET RACKS & BOLLARDS
# ==========================================
# Rack positions along X (leaving gaps at x in [-6, 2] for junction/cross-aisles)
rack_xs = [-34, -26, -18, -10, 8, 16, 24, 32]

# Left side racking row (y = 5.6)
for i, rx in enumerate(rack_xs):
    shelf_type = "ShelfD_01" if i % 2 == 0 else "ShelfE_01"
    # Shelves are 2.6m wide, yaw=1.5708 aligns length along X
    elements.append(include_model(f"rack_L_{i}", f"model://aws_robomaker_warehouse_{shelf_type}", rx, 5.6, 0.0, 1.5708))
    # Safety bollards protecting rack ends
    if i in (0, 3, 4, 7):
        bx = rx - 1.6 if i in (0, 4) else rx + 1.6
        elements.append(bollard(f"bollard_L_{i}", bx, 4.6))

# Right side racking row (y = -5.6)
for i, rx in enumerate(rack_xs):
    shelf_type = "ShelfE_01" if i % 2 == 0 else "ShelfF_01"
    elements.append(include_model(f"rack_R_{i}", f"model://aws_robomaker_warehouse_{shelf_type}", rx, -5.6, 0.0, 1.5708))
    if i in (0, 3, 4, 7):
        bx = rx - 1.6 if i in (0, 4) else rx + 1.6
        elements.append(bollard(f"bollard_R_{i}", bx, -4.6))

# ==========================================
# 5. SIDE SCENERY & CLUTTER (NON-OBSTACLES)
# ==========================================
# Staged pallet jacks, clutter stacks, and trash cans along the outer rack alleys (|y| >= 8.5)
elements.append(include_model("pallet_jack_1", "model://aws_robomaker_warehouse_PalletJackB_01", -22.0, 9.5, 0.02, 0.4))
elements.append(include_model("pallet_jack_2", "model://aws_robomaker_warehouse_PalletJackB_01", 18.0, -9.5, 0.02, 2.8))

elements.append(include_model("clutter_1", "model://aws_robomaker_warehouse_ClutteringA_01", -30.0, 10.0, 0.0, 0.0))
elements.append(include_model("clutter_2", "model://aws_robomaker_warehouse_ClutteringC_01", 10.0, 9.8, 0.0, 1.57))
elements.append(include_model("clutter_3", "model://aws_robomaker_warehouse_ClutteringD_01", -14.0, -10.0, 0.0, 0.0))
elements.append(include_model("clutter_4", "model://aws_robomaker_warehouse_ClutteringA_01", 28.0, -10.0, 0.0, -1.57))

elements.append(include_model("trashcan_1", "model://aws_robomaker_warehouse_TrashCanC_01", -2.0, 8.5, 0.0, 0.0))
elements.append(include_model("trashcan_2", "model://aws_robomaker_warehouse_TrashCanC_01", 2.0, -8.5, 0.0, 3.14))

elements.append(include_model("corner_dumpster_1", "model://dumpster", -41.0, 12.0, 0.0, 0.0))
elements.append(include_model("corner_dumpster_2", "model://dumpster", 41.0, -12.0, 0.0, 3.14))

# Background warehouse workers in side alleys (outside the robot corridor)
elements.append(include_model("worker_side_1", "model://person_standing", -16.0, 9.5, 0.0, 1.2))
elements.append(include_model("worker_side_2", "model://person_standing", 12.0, -9.5, 0.0, -0.8))

# ==========================================
# 6. IN-PATH REALISTIC WAREHOUSE OBSTACLES
# ==========================================
# The robot navigates from x = -38 to x = +40 along y = 0.
# Obstacles are placed with realistic clearance to challenge avoidance and recovery:

# Obstacle 1: Euro-pallet with stacked shipping boxes staged on the right (x = -24.0, y = -1.25)
elements.append(include_model("obs1_pallet", "model://euro_pallet", -24.0, -1.25, 0.0, 0.0))
elements.append(include_model("obs1_box1", "model://cardboard_box", -24.15, -1.25, 0.20, 0.1))
elements.append(include_model("obs1_box2", "model://cardboard_box", -23.85, -1.25, 0.20, -0.15))
elements.append(include_model("obs1_box3", "model://cardboard_box", -24.0, -1.25, 0.50, 0.05))

# Obstacle 2: Warehouse worker standing in the left corridor checking inventory (x = -12.0, y = 1.35)
elements.append(include_model("obs2_worker", "model://person_standing", -12.0, 1.35, 0.0, -1.57))

# Obstacle 3: Industrial high-visibility construction barrel in center aisle (x = 2.0, y = 0.0)
# (Requires robot to detect center blockage, slow down, rotate to clear path, and shift lane)
elements.append(include_model("obs3_hazard_barrel", "model://construction_barrel", 2.0, 0.0, 0.0, 0.0))

# Obstacle 4: Utility picking cart on the left side (x = 16.0, y = 1.35)
elements.append(include_model("obs4_utility_cart", "model://utility_cart", 16.0, 1.35, 0.0, 1.57))

# Obstacle 5: Staged euro-pallet with shipping boxes on the right side (x = 28.0, y = -1.25)
elements.append(include_model("obs5_pallet", "model://euro_pallet", 28.0, -1.25, 0.0, 0.2))
elements.append(include_model("obs5_box1", "model://cardboard_box", 28.0, -1.25, 0.20, 0.0))
elements.append(include_model("obs5_box2", "model://cardboard_box", 28.0, -1.25, 0.50, 0.3))

# ==========================================
# 7. GOAL: HIGH-VISIBILITY AGV DOCKING STATION
# ==========================================
elements.append(box_model("agv_dock_pad", 40.0, 0.0, 0.02, 3.6, 3.6, 0.04, mat_color(0.1, 0.75, 0.2, spec=0.6), col=False))
elements.append(box_model("agv_dock_beacon", 40.0, 0.0, 0.7, 0.25, 0.25, 1.4, mat_color(0.1, 0.9, 0.25, spec=0.9), col=True))

body_xml = "\n    ".join(elements)

world_xml = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="warehouse">
    <include><uri>model://sun</uri></include>
    <include><uri>model://ground_plane</uri></include>

    <!-- Balanced Industrial Lighting -->
    <light name="main_sunlight" type="directional">
      <pose>0 0 16 0 0 0</pose>
      <diffuse>0.85 0.85 0.88 1</diffuse>
      <specular>0.25 0.25 0.25 1</specular>
      <direction>-0.25 0.25 -1</direction>
      <cast_shadows>true</cast_shadows>
    </light>

    <light name="aisle_light_1" type="point">
      <pose>-24 0 7.5 0 0 0</pose>
      <diffuse>0.75 0.75 0.72 1</diffuse>
      <attenuation><range>40</range><linear>0.02</linear><constant>0.35</constant></attenuation>
      <cast_shadows>false</cast_shadows>
    </light>

    <light name="aisle_light_2" type="point">
      <pose>-8 0 7.5 0 0 0</pose>
      <diffuse>0.75 0.75 0.72 1</diffuse>
      <attenuation><range>40</range><linear>0.02</linear><constant>0.35</constant></attenuation>
      <cast_shadows>false</cast_shadows>
    </light>

    <light name="aisle_light_3" type="point">
      <pose>8 0 7.5 0 0 0</pose>
      <diffuse>0.75 0.75 0.72 1</diffuse>
      <attenuation><range>40</range><linear>0.02</linear><constant>0.35</constant></attenuation>
      <cast_shadows>false</cast_shadows>
    </light>

    <light name="aisle_light_4" type="point">
      <pose>24 0 7.5 0 0 0</pose>
      <diffuse>0.75 0.75 0.72 1</diffuse>
      <attenuation><range>40</range><linear>0.02</linear><constant>0.35</constant></attenuation>
      <cast_shadows>false</cast_shadows>
    </light>

    <scene>
      <ambient>0.62 0.62 0.62 1</ambient>
      <background>0.75 0.78 0.82 1</background>
      <shadows>true</shadows>
    </scene>

    {body_xml}

    <physics name="ode_physics" default="0" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>
  </world>
</sdf>
"""

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "warehouse.world")
with open(out_path, "w") as f:
    f.write(world_xml)
print(f"Generated realistic warehouse world at: {out_path} ({len(world_xml)} bytes)")
