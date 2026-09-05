#!/usr/bin/env python3
"""
All-in-one ROS 2 Launch File for Differential Drive Robot Simulation
in Realistic Industrial Warehouse Environment.
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    world_path = os.path.join(pkg_dir, 'warehouse.world')
    urdf_path = os.path.join(pkg_dir, 'urdf', 'Assem_Final_1.urdf')
    navigator_script = os.path.join(pkg_dir, 'yolo_camera_navigator.py')

    gazebo_models_path = os.path.expanduser('~/gazebo_models')
    aws_models_path = os.path.expanduser('~/ros2_ws/install/aws_robomaker_small_warehouse_world/share/aws_robomaker_small_warehouse_world/models')
    local_assets_path = os.path.join(pkg_dir, 'warehouse_assets')
    user_gazebo_models = os.path.expanduser('~/.gazebo/models')

    current_model_path = os.environ.get('GAZEBO_MODEL_PATH', '')
    combined_model_path = f"{local_assets_path}:{user_gazebo_models}:{gazebo_models_path}:{aws_models_path}:{current_model_path}"

    set_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=combined_model_path
    )

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    start_navigator = LaunchConfiguration('start_navigator', default='true')
    start_rqt = LaunchConfiguration('start_rqt', default='true')

    declare_use_sim_time = DeclareLaunchArgument('use_sim_time', default_value='true')
    declare_start_navigator = DeclareLaunchArgument('start_navigator', default_value='true')
    declare_start_rqt = DeclareLaunchArgument('start_rqt', default_value='true')

    # Gazebo launch
    gazebo_ros_dir = get_package_share_directory('gazebo_ros')
    gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros_dir, 'launch', 'gazebo.launch.py')),
        launch_arguments={'world': world_path}.items()
    )

    # Spawn robot entity at starting location (-38, 0, 0.6)
    spawn_robot_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'autonomous_robot',
            '-file', urdf_path,
            '-x', '-38.0',
            '-y', '0.0',
            '-z', '0.6'
        ],
        output='screen'
    )

    # YOLO Camera Navigator node
    navigator_cmd = ExecuteProcess(
        cmd=[
            'python3', navigator_script,
            '--ros-args',
            '-p', 'goal_x:=40.0',
            '-p', 'goal_y:=0.0',
            '-p', 'use_sim_time:=true'
        ],
        output='screen',
        condition=IfCondition(start_navigator)
    )

    # Rqt Image View
    rqt_cmd = ExecuteProcess(
        cmd=['ros2', 'run', 'rqt_image_view', 'rqt_image_view', '/yolo_debug/image'],
        output='screen',
        condition=IfCondition(start_rqt)
    )

    ld = LaunchDescription()
    ld.add_action(set_model_path)
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_start_navigator)
    ld.add_action(declare_start_rqt)
    ld.add_action(gazebo_cmd)
    ld.add_action(spawn_robot_cmd)
    ld.add_action(navigator_cmd)
    ld.add_action(rqt_cmd)

    return ld
