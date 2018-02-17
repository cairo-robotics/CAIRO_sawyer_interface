#!/usr/bin/env python2
'''
Sawyer class wrapper for creating various servers to send commands to sawyer
'''
import rospy
import moveit_commander
import sys
import moveit_msgs.msg
import geometry_msgs.msg
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseArray
from std_msgs.msg import String
from std_msgs.msg import Float32MultiArray
from cairo_sawyer_interface.srv import ForwardKinematics
from forward_kinematics.forward_kinematic_client import ForwardKinematicsClient


class SawyerServer(object):
    '''creat various servers for reading in pose and joint data and moving
    sawyer accordingly'''

    def __init__(self, PLANNING_GROUP="right_arm",
                 sub_pose_topic="/commander/pose",
                 sub_pose_array_topic="/commander/pose_array",
                 sub_joint_state_topic="/commander/joint_state",
                 pub_topic="/test_topic"):
        '''creates subs pubs and moveit_commander groups'''

        self.sub_pose = rospy.Subscriber(sub_pose_topic, Pose,
                                         self._moveit_pose_callback,
                                         queue_size=1)
        self.sub_pose_array = rospy.Subscriber(sub_pose_array_topic, PoseArray,
                                               self._moveit_pose_array_callback,
                                               queue_size=1)
        self.sub_joint_state=rospy.Subscriber(sub_joint_state_topic,
                                              Float32MultiArray,
                                              self._moveit_joint_state_callback,
                                              queue_size=1)
        self.diagnostic = rospy.Publisher(pub_topic, String, queue_size=1)
        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()
        self.group = moveit_commander.MoveGroupCommander(PLANNING_GROUP)
        self.fk_client = ForwardKinematicsClient()

    def _moveit_pose_callback(self, pose):
        '''pose callback function'''
        self.group.set_pose_target(pose)
        self.plan = self.group.plan()
        self.group.go()
        self.diagnostic.publish("future completion status message")

    def _moveit_pose_array_callback(self, pose_array):
        '''use an array of poses to creat waypoints for path plannner'''
        #TODO this still needs work
        waypoints = []
        for i in range(len(pose_array.poses)):
            waypoints.append(pose_array.poses[i])
            print i

        print "first"
        print waypoints[0]
        plan3 = self.group.plan(waypoints)
        self.group.execute(plan3)
        print "last:"
        print waypoints[9]

    def _moveit_joint_state_callback(self, joint_states):
        '''joint state callback function'''
        print("called joint state")
        self.group.clear_pose_targets()
        self.group.set_joint_value_target(joint_states.data)
        self.group.go()
        self.diagnostic.publish("future completion status message")


    #added methods b/c unable to inherit moveit_commander to sawyer_class
    #TODO find a better way? my guess is that there multiple classes to inherit
    def set_pose_target(self, pose):
        '''set the pose target using the MoveGroupCommander'''
        self.group.set_pose_target(pose)

    def set_joint_target(self, joints):
        '''set the joint targets using the MoveGroupCommander'''
        self.group.set_pose_target(pose)

    def plan(self):
        '''set the pose plan using the MoveGroupCommander'''
        self.plan = self.group.plan()

    def execute(self):
        '''execute the plan using MoveGroupCommander'''
        self.group.execute(plan)

    def move_to_planned_pose_target(self, pose):
        '''use pose to set target, plan, and execute'''
        self.set_pose_target(pose)
        self.plan()
        rospy.sleep(4)
        self.group.execute(self.plan)

    def move_to__planned_joint_target(self, joints):
        '''use pose to set target, plan, and execute'''
        self.set_pose_target(pose)
        self.plan()
        self.group.execute(self.plan)

    def get_end_effector_pose(self, joint_positions):
        try:
            joints = Float32MultiArray()
            joints.data = point.positions
            response = self.fk_service(joints)
            return response
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e

    def get_plan_poses(self, plan):
        end_effector_poses = []
        for point in plan.joint_trajectory.points:
            raw_pose = self.get_end_effector_pose(point.positions)
            pose = {
                "position": [x for x in raw_pose["position"]]
                "orientation" = [x for x in raw_pose["orientation"]]
            }
            end_effector_poses.append(pose)
        return end_effector_poses

def test():
    '''testing new functionality NOT UNIT TEST'''
    rospy.init_node('sawyer_commander')
    bender = SawyerServer()
    bender.group.clear_pose_targets()
    group_variable_values = [0.0] * 7
    group_variable_values[0] = -0.4
    group_variable_values[1] = 1.0
    group_variable_values[2] = -3.0
    group_variable_values[3] = 2.
    group_variable_values[4] = -0.1
    group_variable_values[5] = 0.5
    group_variable_values[6] = -1
    #group_variable_values[7] = -0.0416

    bender.group.set_joint_value_target(group_variable_values)

    bender.plan()
    bender.get_plan_end_effector_poses(bender.plan)
    print(bender.plan.joint_trajectory.points)
    # bender.group.go()


def main():
    print "run sawyer interface server.py"

if __name__ == '__main__':
    test()
