# Differential Drive Autonomous Robot with Camera-Based Obstacle Detection

A ROS 2 (Humble) simulation package featuring an autonomous differential drive robot operating in a Gazebo warehouse world with YOLO camera-based obstacle avoidance and navigation.

---

## 📋 Run Commands & Quick Start

### 1. Clean Up Previous Processes
```bash
pkill -9 gzserver; pkill -9 gzclient; pkill -9 gazebo
pkill -9 -f yolo_camera_navigator.py
pkill -9 -f rqt_image_view
sleep 3
```

### 2. Terminal 1 — Launch Gazebo + Warehouse
```bash
source /opt/ros/humble/setup.bash
ros2 launch gazebo_ros gazebo.launch.py world:=warehouse.world
```

### 3. Terminal 2 — Spawn Robot
```bash
source /opt/ros/humble/setup.bash
cd urdf
ros2 run gazebo_ros spawn_entity.py -entity autonomous_robot -file Assem_Final_1.urdf -x -38 -y 0 -z 0.6
```

### 4. Terminal 3 — Navigate to the Goal
```bash
source /opt/ros/humble/setup.bash
python3 yolo_camera_navigator.py --ros-args -p goal_x:=40.0 -p goal_y:=0.0 -p use_sim_time:=true
```

### 5. Terminal 4 — YOLO Detection View
```bash
source /opt/ros/humble/setup.bash
ros2 run rqt_image_view rqt_image_view /yolo_debug/image
```

---

## 📁 Repository Structure
- `urdf/`: Robot description files (`Assem_Final_1.urdf`) and YOLO weights (`yolov8n.pt`).
- `meshes/`: STL 3D models for base link, wheels, and camera.
- `worlds/` & `warehouse.world`: Gazebo simulation environments.
- `launch/`: ROS 2 launch files.
- `config/`: Joint configurations.
- `yolo_camera_navigator.py`: Python navigation and obstacle avoidance script using YOLO.
- `differential_drive_robot_run_commands.txt`: Raw run commands reference.
