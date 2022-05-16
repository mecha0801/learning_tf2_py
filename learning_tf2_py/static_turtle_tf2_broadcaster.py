# Copyright 2021 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

from geometry_msgs.msg import TransformStamped  #? transformation tree에 게시할 메시지에 대한 템플릿이 제공된다?

import rclpy
from rclpy.node import Node

# tf2_ros 패키지는 정적변환을 쉽게 게시하도록 "StaticTransformBroadcaster"을 제공함
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster

import tf_transformations   # 오일러 각도를 사분원으로 변환하는 함수를 제공함


class StaticFramePublisher(Node):   # StaticFramePublisher라는 이름의 생성자
    """
    Broadcast transforms that never change.

    This example publishes transforms from `world` to a static turtle frame.
    The transforms are only published once at startup, and are constant for all
    time.
    """

    def __init__(self, transformation): # node를 static_turtle_tf2_broadcaster라는 이름으로 초기화
        super().__init__('static_turtle_tf2_broadcaster')

        self._tf_publisher = StaticTransformBroadcaster(self)   # node가 초기화 되면 생성되어 시작 시 하나의 정적 변환(static transformation)을 전송

        # Publish static transforms once at startup
        self.make_transforms(transformation)

    def make_transforms(self, transformation):
        static_transformStamped = TransformStamped()    #? publishing 중인 transform에 timestamp를 찍어야함
        static_transformStamped.header.stamp = self.get_clock().now().to_msg()  #? 현재 시간으로 timestamp를 찍음
        static_transformStamped.header.frame_id = 'world'   # link의 부모 프레임(상위 프레임) 이름 설정
        static_transformStamped.child_frame_id = sys.argv[1]    # link의 자식 프레임(하위 프레임) 이름 설정
        # 아래는 6D pose (변환과 회전)
        static_transformStamped.transform.translation.x = float(sys.argv[2])
        static_transformStamped.transform.translation.y = float(sys.argv[3])
        static_transformStamped.transform.translation.z = float(sys.argv[4])
        quat = tf_transformations.quaternion_from_euler(float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7]))
        static_transformStamped.transform.rotation.x = quat[0]
        static_transformStamped.transform.rotation.y = quat[1]
        static_transformStamped.transform.rotation.z = quat[2]
        static_transformStamped.transform.rotation.w = quat[3]

        self._tf_publisher.sendTransform(static_transformStamped)   # 정적 변환을 broadcast


def main():
    logger = rclpy.logging.get_logger('logger')

    # obtain parameters from command line arguments
    if len(sys.argv) < 8:
        logger.info('Invalid number of parameters. Usage: \n'
                    '$ ros2 run turtle_tf2_py static_turtle_tf2_broadcaster'
                    'child_frame_name x y z roll pitch yaw')
        sys.exit(0)
    else:
        if sys.argv[1] == 'world':
            logger.info('Your static turtle name cannot be "world"')
            sys.exit(0)

    # pass parameters and initialize node
    rclpy.init()
    node = StaticFramePublisher(sys.argv)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()
