#!/usr/bin/env bash
# ==============================================================================
# One-Click Autonomous Differential Drive Robot Simulation Runner
# ==============================================================================
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "=== Cleaning up previous simulation processes ==="
pkill -9 -f gzserver 2>/dev/null || true
pkill -9 -f gzclient 2>/dev/null || true
pkill -9 -f gazebo 2>/dev/null || true
pkill -9 -f yolo_camera_navigator.py 2>/dev/null || true
pkill -9 -f rqt_image_view 2>/dev/null || true
sleep 2

echo "=== Sourcing ROS 2 Humble ==="
source /opt/ros/humble/setup.bash
if [ -f "$HOME/ros2_ws/install/setup.bash" ]; then
    source "$HOME/ros2_ws/install/setup.bash"
fi

export GAZEBO_MODEL_PATH="$DIR/warehouse_assets:$HOME/.gazebo/models:$HOME/gazebo_models:$HOME/ros2_ws/install/aws_robomaker_small_warehouse_world/share/aws_robomaker_small_warehouse_world/models:$GAZEBO_MODEL_PATH"

echo "=== Launching Gazebo Warehouse Simulation ==="
ros2 launch gazebo_ros gazebo.launch.py world:="$DIR/warehouse.world" &
GAZEBO_PID=$!

echo "Waiting for Gazebo to initialize..."
until ros2 service list 2>/dev/null | grep -q "/spawn_entity"; do
    sleep 1
done
echo "Gazebo initialized."

echo "=== Spawning Autonomous Robot at (-38, 0, 0.6) ==="
ros2 run gazebo_ros spawn_entity.py -entity autonomous_robot -file "$DIR/urdf/Assem_Final_1.urdf" -x -38.0 -y 0.0 -z 0.6

echo "=== Starting YOLO Camera Detection View ==="
ros2 run rqt_image_view rqt_image_view /yolo_debug/image &

echo "=== Starting Autonomous YOLO Camera Navigator (Goal: 40.0, 0.0) ==="
python3 "$DIR/yolo_camera_navigator.py" --ros-args -p goal_x:=40.0 -p goal_y:=0.0 -p use_sim_time:=true
