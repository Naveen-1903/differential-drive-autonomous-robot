# Differential Drive Autonomous Robot with Camera-Based Obstacle Detection

An advanced ROS 2 (Humble) simulation of an autonomous differential drive robot operating in a photorealistic Gazebo warehouse environment using camera-based YOLOv8 obstacle detection and intelligent corridor navigation.

---

## 🌟 Key Features

- **Photorealistic Industrial Warehouse Environment**:
  - High-resolution concrete flooring with expansion joints and specular reflection.
  - OSHA-standard $45^\circ$ yellow & black caution hazard stripes along the AGV driving corridor.
  - Multi-tier industrial pallet racks loaded with realistic merchandise (AWS RoboMaker `ShelfD_01`, `ShelfE_01`, `ShelfF_01`).
  - Corrugated industrial steel walls with protective kick-plates, safety signs, and sectional overhead loading dock doors.
  - Steel ceiling cross-trusses and high-bay LED daylight illumination fixtures.
  - Impact safety bollards protecting rack corners.
- **Autonomous Vision-Guided Navigation ([`yolo_camera_navigator.py`](yolo_camera_navigator.py))**:
  - **Multi-Modal Obstacle Detection**: Dual YOLOv8 deep learning detection + OpenCV color-blob contour analysis.
  - **Corridor Overlap Registration**: Automatically detects obstacles intruding into the forward trajectory and calculates optimal side lane offsets (`lane_offset = 2.2 m`).
  - **Timed Straight Reverse & In-Place Clearing Turn**: When facing proximity blockage (`C >= rev_threshold`) or progress halts (`stuck_window`), the robot backs straight away without tail swing collisions and rotates in place until its camera verifies the path ahead is clear.
  - **Smooth Heading Control**: Eliminates zigzag oscillations using aisle centerline lookahead tracking and low-pass steering rate limits.

---

## 🚀 Quick Start

### Option A: One-Click Execution (Recommended)
Simply execute the automated runner script from the repository root:
```bash
cd ~/Downloads/Assem_Final_1
./run_simulation.sh
```

---

### Option B: Step-by-Step Multi-Terminal Execution

#### 1. Clean Up Previous Instances
```bash
pkill -9 gzserver; pkill -9 gzclient; pkill -9 gazebo
pkill -9 -f yolo_camera_navigator.py
pkill -9 -f rqt_image_view
sleep 2
```

#### 2. Terminal 1 — Launch Gazebo Warehouse
```bash
source /opt/ros/humble/setup.bash
export GAZEBO_MODEL_PATH=~/Downloads/Assem_Final_1/warehouse_assets:~/.gazebo/models:~/gazebo_models:~/ros2_ws/install/aws_robomaker_small_warehouse_world/share/aws_robomaker_small_warehouse_world/models:$GAZEBO_MODEL_PATH
ros2 launch gazebo_ros gazebo.launch.py world:=warehouse.world
```

#### 3. Terminal 2 — Spawn Autonomous Robot
```bash
source /opt/ros/humble/setup.bash
cd urdf
ros2 run gazebo_ros spawn_entity.py -entity autonomous_robot -file Assem_Final_1.urdf -x -38 -y 0 -z 0.6
```

#### 4. Terminal 3 — Run YOLO Camera Navigator
```bash
source /opt/ros/humble/setup.bash
python3 yolo_camera_navigator.py --ros-args -p goal_x:=40.0 -p goal_y:=0.0 -p use_sim_time:=true
```

#### 5. Terminal 4 — Live YOLO Detection Camera View
```bash
source /opt/ros/humble/setup.bash
ros2 run rqt_image_view rqt_image_view /yolo_debug/image
```

---

## 📁 Repository Structure

```
├── warehouse.world                  # Complete photorealistic warehouse simulation world
├── make_world.py                    # Procedural generator for warehouse geometry and assets
├── warehouse_assets/                # PBR textures, scripts, and Gazebo model definition
│   ├── materials/
│   │   ├── scripts/warehouse.material
│   │   └── textures/                # High-res concrete, hazard stripes, corrugated wall, dock doors
│   ├── model.config
│   └── model.sdf
├── yolo_camera_navigator.py         # Autonomous ROS 2 navigation node with YOLOv8 & blob detection
├── run_simulation.sh                # Automated one-click simulation launcher
├── differential_drive_robot_run_commands.txt # Reference commands list
├── launch/
│   └── warehouse_simulation.launch.py # All-in-one ROS 2 Python launch file
├── urdf/
│   ├── Assem_Final_1.urdf           # Robot URDF model with differential drive plugin & camera sensor
│   └── Assem_Final_1.csv
├── meshes/                          # High-accuracy STL meshes for chassis, wheels, and camera
└── config/                          # YAML joint configurations
```
