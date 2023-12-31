#!/usr/bin/env python3

import py_trees as pt
import py_trees_ros as ptr
import rclpy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
from sensor_msgs.msg import LaserScan,Joy
#from sensor_msgs.msg import Joy
import numpy as np
import pandas as pd
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from autonomous_map_navigate.utilities import *
import math
import time




class rotate(pt.behaviour.Behaviour):

    """
    Rotates the robot about z-axis 
    """

    def __init__(self, name="rotate platform", topic_name="/cmd_vel", direction=1, max_ang_vel=1.0):

        # self.logger.info("[ROTATE] initialising rotate behavior")

        # Set up topic name to publish rotation commands
        self.topic_name = topic_name

        # Set up Maximum allowable rotational velocity
        self.max_ang_vel = max_ang_vel # units: rad/sec

        # Set up direction of rotation
        self.direction = direction

        # Execution checker
        self.sent_goal = False

        # become a behaviour
        super(rotate, self).__init__(name)

    def setup(self, **kwargs):
        """
        Setting up things which generally might require time to prevent delay in tree initialisation
        """
        self.logger.info("[ROTATE] setting up rotate behavior")
        
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        # Create publisher to publish rotation commands
        self.cmd_vel_pub = self.node.create_publisher(
            msg_type=Twist,
            topic=self.topic_name,
            qos_profile=ptr.utilities.qos_profile_latched()
        )

        self.feedback_message = "setup"
        return True

    def update(self):
        """
        Primary function of the behavior is implemented in this method

        Rotating the robot at maximum allowed angular velocity in a given direction, 
        where, if **direction** is +1, it implies clockwise rotation, and if it is -1, it implies
        counter-clockwise rotation
        """
        self.logger.info("[ROTATE] update: updating rotate behavior")
        self.logger.debug("%s.update()" % self.__class__.__name__)

        # Send the rotation command to self.topic_name in this method using the message type Twist()
        
        msg = Twist()
        msg.angular.z = 0.5
        """if (self.direction == +1):
        	msg.angular.z = 0.5
        elif (self.direction == -1):
        	msg.angular.z = - 0.5
        """
        self.cmd_vel_pub.publish(msg)
        
        ## YOUR CODE HERE ##
        
        return pt.common.Status.RUNNING

    def terminate(self, new_status):
        """
        terminate() is trigerred once the execution of the behavior finishes, 
        i.e. when the status changes from RUNNING to SUCCESS or FAILURE
        """
        self.logger.info("[ROTATE] terminate: publishing zero angular velocity")
        twist_msg = Twist()
        twist_msg.linear.x = 0.
        twist_msg.linear.y = 0.
        twist_msg.angular.z = 0.
                    
        self.cmd_vel_pub.publish(twist_msg)
        self.sent_goal = False
        return super().terminate(new_status)

class stop_motion(pt.behaviour.Behaviour):

    """
    Stops the robot when it is controlled using joystick or by cmd_vel command
    """

    def __init__(self, 
                 name: str="stop platform", 
                 topic_name1: str="/cmd_vel", 
                 topic_name2: str="/joy"):
        super(stop_motion, self).__init__(name)
        # Set up topic name to publish rotation commands
        self.cmd_vel_topic = topic_name1
        self.joy_topic = topic_name2
        
        
       

    def setup(self, **kwargs):
        """
        Setting up things which generally might require time to prevent delay in tree initialisation
        """
        self.logger.info("[STOP MOTION] setting up stop motion behavior")

        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        # Create publisher to publish rotation commands
        self.cmd_vel_topic = self.node.create_publisher(
            msg_type=Twist,
            topic=self.cmd_vel_topic,
            qos_profile=ptr.utilities.qos_profile_latched()
        )

        # Create publisher to override joystick commands
        self.joy_pub = self.node.create_publisher(
            msg_type=Joy,
            topic=self.joy_topic,
            qos_profile=ptr.utilities.qos_profile_latched()
        )
        
        self.feedback_message = "setup"
        return True

    def update(self):
        """
        Primary function of the behavior is implemented in this method

        Rotating the robot at maximum allowed angular velocity in a given direction, 
        where if _direction_ is +1, it implies clockwise rotation, and if it is -1, it implies
        counter-clockwise rotation
        """
        self.logger.info("[STOP] update: updating stop behavior")
        self.logger.debug("%s.update()" % self.__class__.__name__)

        """
        Send the zero rotation command to self.cmd_vel_topic
        """
        
        ## YOUR CODE HERE ##
       # self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        msg1 = Twist()
        msg1.linear.x = 0.0
        msg1.linear.x = 0.0
        # msg1.angular.z = 0.0
        self.cmd_vel_topic.publish(msg1)

           
        



        """
        sending self.joy_pub in this method. The frame_id for Joy() message is
        "/dev/input/js0". It is similar to just pressing the deadman button on the joystick.
        Nothing to implement here.
        """
        ## Uncomment the following lines to publish Joy() message when running on the robot ##
        # joyMessage = Joy()
        # joyMessage.header.frame_id = "/dev/input/js0"
        # joyMessage.axes = [0., 0., 0., 0., 0., 0.]
        # joyMessage.buttons = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
        # self.joy_pub.publish(joyMessage)   
             
        return pt.common.Status.SUCCESS
        # return pt.common.Status.RUNNING


    def terminate(self, new_status):
        """
        terminate() is trigerred once the execution of the behavior finishes, 
        i.e. when the status changes from RUNNING to SUCCESS or FAILURE
        """
        self.logger.info("[ROTATE] terminate: publishing zero angular velocity")
        twist_msg = Twist()
        twist_msg.linear.x = 0.
        twist_msg.linear.y = 0.
        twist_msg.angular.z = 0.

       
                    
        self.cmd_vel_topic.publish(twist_msg)
        self.sent_goal = False
        return super().terminate(new_status)

class battery_status2bb(ptr.subscribers.ToBlackboard):

    """
    Checking battery status
    """
    def __init__(self, 
                 topic_name: str="/battery_voltage",
                 name: str=pt.common.Name.AUTO_GENERATED, 
                 threshold: float=30.0):
        super().__init__(name=name,
                        topic_name=topic_name,
                        topic_type=Float32,
                        blackboard_variables={'battery': 'data'},
                        initialise_variables={'battery': 100.0},
                        clearing_policy=pt.common.ClearingPolicy.NEVER,  # to decide when data should be cleared/reset.
                        qos_profile=ptr.utilities.qos_profile_unlatched()
                        )
        self.blackboard.register_key(
            key='battery_low_warning',
            access=pt.common.Access.WRITE
        ) 
        self.blackboard.battery_low_warning = False   # decision making
        self.threshold = threshold

    def update(self):
        """
        Primary function of the behavior is implemented in this method

        Call the parent to write the raw data to the blackboard and then check against the
        threshold to determine if the low warning flag should also be updated.
        """
        self.logger.info('[BATTERY] update: running batter_status2bb update')
        self.logger.debug("%s.update()" % self.__class__.__name__)
        status = super(battery_status2bb, self).update()
        
        """
        check battery voltage level stored in self.blackboard.battery. By comparing with threshold value, update the value of 
        self.blackboad.battery_low_warning
        """

        ## YOUR CODE HERE ##
        
        
        if self.blackboard.battery < self.threshold:
            self.blackboard.battery_low_warning = True
        else:
            self.blackboard.battery_low_warning = False
                
        return pt.common.Status.SUCCESS

class laser_scan_2bb(ptr.subscribers.ToBlackboard):

    """
    Checking laser_scan to avoid possible collison
    """
    def __init__(self, 
                 topic_name: str="/scan", #/sick_lms_1xx/scan for robile3
                 name: str=pt.common.Name.AUTO_GENERATED, 
                 safe_range: float= 0.3):
        super().__init__(name=name,
                        topic_name=topic_name,
                        topic_type=LaserScan,
                        blackboard_variables={'laser_scan':'ranges'},
                 topic_name: str="/sick_lms_1xx/scan",  # topic = "/scan" for simulation
                 name: str=pt.common.Name.AUTO_GENERATED, 
                 safe_range: float=1.5):
        super().__init__(name=name,
                        topic_name=topic_name,
                        topic_type=LaserScan,
                        blackboard_variables={'laser_scan':'ranges'},  
                        #initialise_variables={'battery': []},
                        clearing_policy=pt.common.ClearingPolicy.NEVER,  # to decide when data should be cleared/reset.
                        # qos_profile=QoSReliabilityPolicy.RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT
                        qos_profile=QoSProfile(
                                    reliability=QoSReliabilityPolicy.RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT,
                                    history=QoSHistoryPolicy.RMW_QOS_POLICY_HISTORY_KEEP_LAST,
                                    depth=10
                                )
                        )
        #self.blackboard=pt.blackboard.Blackboard()
        self.blackboard.register_key(
            key='collison_warning',
            access=pt.common.Access.WRITE
        )
        self.blackboard.register_key(
            key='point_at_min_dist',
            access=pt.common.Access.WRITE
        )
        # self.blackboard.register_key(
        #     key='counter',
        #     access=pt.common.Access.WRITE
        # )

        self.blackboard.register_key(
            key='wall_warn',
            access=pt.common.Access.WRITE
        )

        self.blackboard.register_key(
            key='perp_dis',
            access=pt.common.Access.WRITE
        )

        self.blackboard.register_key(
            key='slope',
            access=pt.common.Access.WRITE
        )

        self.blackboard.register_key(
            key='rotate_dir',
            access=pt.common.Access.WRITE
        )

        self.blackboard.register_key(
            key='aligned',
            access=pt.common.Access.WRITE
        )

        # self.blackboard.register_key(
        #     key='angle_of_rotation',
        #     access=pt.common.Access.WRITE
        # )
        self.blackboard.register_key(
            key='near_distance',
            access=pt.common.Access.WRITE
        )
        self.blackboard.register_key(
            key='fix_wall',
            access=pt.common.Access.WRITE
        )
        # self.blackboard.register_key(
        #     key='new_wall',
        #     access=pt.common.Access.WRITE
        # )
        self.blackboard.register_key(
            key='fix_wall_warn',
            access=pt.common.Access.WRITE
        )
        self.blackboard.register_key(
            key='wall',
            access=pt.common.Access.WRITE
        )


        self.blackboard.wall_warn = False

        self.blackboard.perp_dis = 0.0
        self.blackboard.near_distance = 0.0

        self.blackboard.slope = 0.0
        self.blackboard.rotate_dir = 'default'
        self.blackboard.fix_wall_warn = False
        self.blackboard.aligned = False
        self.blackboard.wall= None 
    

        

        # self.blackboard.counter = 0
        self.blackboard.collison_warning = False   # decision making
        self.safe_min_range = safe_range
        self.blackboard.point_at_min_dist = 0.0
        

    def update(self):
        self.blackboard.register_key(
            key='counter',
            access=pt.common.Access.WRITE
        )

        self.blackboard.counter = 0
        self.blackboard.collison_warning = False   # decision making
        self.safe_min_range = safe_range
        self.blackboard.point_at_min_dist = 0.0
  
    def update(self):
        """
        Primary function of the behavior is implemented in this method
        Call the parent to write the raw data to the blackboard and then check against the
        threshold to set the warning if the robot is close to any obstacle.
        """
        self.logger.info("[LASER SCAN] update: running laser_scan_2bb update")
        self.logger.debug("%s.update()" % self.__class__.__name__)
        status = super(laser_scan_2bb, self).update()

        """
        Based on the closeness of laser scan points (any of them) to robot, update the value of self.blackboard.collison_warning.
        Assign the minimum value of laser scan to self.blackboard.point_at_min_dist. 
        Note: The min() function can be used to find the minimum value in a list.
        """

        ## YOUR CODE HERE ##   
        # self.blackboard.counter += 1

        if self.blackboard.exists('laser_scan'):
            laser_data = np.array(self.blackboard.laser_scan)
            laser_data[laser_data <= 0.05] = 1.0
            laser_data = np.nan_to_num(laser_data, nan=40)
            laser_data[np.isinf(laser_data)]=50
            # laser_data = laser_data.tolist()

            self.blackboard.point_at_min_dist = min(laser_data)

            if self.blackboard.point_at_min_dist < self.safe_min_range:
                self.blackboard.collison_warning = True
                # self.blackboard.wall_warn = False
                # self.blackboard.aligned = False
            else:
                self.blackboard.collison_warning = False

            data = laser_data

  
            #for simulation
            # red_data = process_data(range_data= data, max_angle= 1.5700000524520874, min_angle= -1.5700000524520874, max_range= 5.599999904632568, min_range= 0.05000000074505806, sigma= 0.15 , rf_max_pts= 4, reduce_bool= True)
                
            #for robile3
            self.red_data = process_data(range_data= data, max_angle= 1.5707963705062866, min_angle= -1.5707963705062866, max_range= 25.0, min_range= 0.05000000074505806, sigma= 0.15 , rf_max_pts= 4, reduce_bool= True)
            # self.res = RANSAC_get_line_params(points= self.red_data, dist_thresh= 0.03, iterations= 450, thresh_count= 8)
            # print(len(self.res))
            # print(self.res)

            # return pt.common.Status.RUNNING 
            

            # filtered_data = median_filter(red_data,k=5)
            if len(self.red_data) <= 2:
                print("No wall Found")
                # self.wall_near = 
                self.blackboard.near_distance = 0.0
                self.blackboard.wall= 'None'
                self.blackboard.fix_wall = 'None'
                self.blackboard.wall_warn = False
            else:
                self.res = RANSAC_get_line_params(points= self.red_data, dist_thresh= 0.02, iterations= 20, thresh_count= 12)
                # self.res = RANSAC_get_line_params(points= self.red_data, dist_thresh= 0.03, iterations= 110, thresh_count= 4)
                print(len(self.res))
                print(self.res)

                if self.res != []:
                    self.d_params = []
                    for entry in self.res:
                        d_par = entry[0]
                        self.d_params.append(d_par)

                        # print(self.d_params)
                    near_dis = min(self.d_params)
                    self.blackboard.near_distance = near_dis
                    self.fix_wall = self.res[self.d_params.index(near_dis)]
                    # self.blackboard.wall= self.wall_near
                    print(self.fix_wall[0], self.fix_wall[1])
                    self.blackboard.fix_wall = self.fix_wall
                    self.blackboard.slope = self.fix_wall[1]
                    self.blackboard.wall_warn = True
                    return pt.common.Status.SUCCESS

                    
        else:
            print("Initiating Laser Scan")
            return pt.common.Status.RUNNING        




        


class move_allign(pt.behaviour.Behaviour):

    """
    Move the robot about x-axis or y-axis untill safe range, then allign parallely to that wall
    """

    def __init__(self, name="move_and_allign", topic_name="/cmd_vel", direction=1, max_ang_vel=0.5):

        self.topic_name = topic_name

        self.max_ang_vel = max_ang_vel # units: rad/sec

        self.direction = direction

        # Execution checker
        self.sent_goal = False
        self.section_executed = False  # Flag to track if the section has been executed


        # become a behaviour
        super(move_allign, self).__init__(name)

        self.blackboard = pt.blackboard.Blackboard()


        self.wall_warn = self.blackboard.get('wall_warn')
        self.distance = self.blackboard.get('near_distance')
        self.slope = self.blackboard.get('slope')
        self.flag = False
        # self.fix_wall = self.blackboard.get('fix_wall')
        # self.aligned = self.blackboard.get('aligned')
        # self.aligned = Fals/e
        # self.res = self.blackboard.get('fix_wall')
    


        

    def setup(self, **kwargs):
        """
        Setting up things which generally might require time to prevent delay in tree initialisation
        """
        self.logger.info("[moving_and_alligning] setting up move_allign behavior")
        
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        # Create publisher to publish rotation commands
        self.cmd_vel_pub = self.node.create_publisher(
            msg_type=Twist,
            topic=self.topic_name,
            qos_profile=ptr.utilities.qos_profile_latched()
        )

        # self.distance = self.blackboard.get('near_distance')

        self.feedback_message = "setup"
        return True

    def update(self):
        """
        Primary function of the behavior is implemented in this method

        Rotating the robot at maximum allowed angular velocity in a given direction, 
        where, if **direction** is +1, it implies clockwise rotation, and if it is -1, it implies
        counter-clockwise rotation
        """
        self.logger.info("[moving_and_alligning] setting up move_allign behavior")
        self.logger.debug("%s.update()" % self.__class__.__name__)
        # self.d = self.blackboard.get('distance')
        self.distance = self.blackboard.get('near_distance')
        self.dir_move = self.blackboard.get('wall')
        self.fix_wall = self.blackboard.get('fix_wall')
        self.slope = self.blackboard.get('slope')
        msg = Twist()
        msg1 = Twist()
        msg2 = Twist()
        msg3 = Twist()
        msg4 = Twist()
        if not self.blackboard.exists('laser_scan'):
            print("waiting")  # Laser data not available yet, keep waiting
            return pt.common.Status.RUNNING 
        else:
            print("laser")
            laser_data = np.array(self.blackboard.get('laser_scan'))
            laser_data[laser_data <= 0.05] = 1.0
            laser_data = np.nan_to_num(laser_data, nan=40)
            laser_data[np.isinf(laser_data)]=50
            if np.all(laser_data == 50):
                self.blackboard.set('wall_warn', False)
            
            # assuming safe distance between robot and wall is 0.5
            self.safe_distance = 0.8
            m_init = self.fix_wall[1]
            c = self.fix_wall[2]  #rotating the robot at the begining based on the Intercept sign
            if c > 0:
                rot_dir = 1.0
            elif c < 0:
                rot_dir = -1.0
            print(m_init)
            if 0.0 < abs(m_init) < 2.0 and self.flag == False:  # first rotation, nearset wall infront of robot
                msg.angular.z = 0.5 * rot_dir
                self.cmd_vel_pub.publish(msg)
                return pt.common.Status.RUNNING 
            
            else:
                print("Perpendicular")
                self.flag = True
                d = self.fix_wall[0]
                if d >= self.safe_distance:
                    msg1.linear.x = 0.1
                    self.cmd_vel_pub.publish(msg1)
                    return pt.common.Status.RUNNING 
                
                else:
                    # math cal to know which direction to rotate based on the longest side of the wall
                    if not self.section_executed:
                        self.d = self.fix_wall[0]
                        self.m = self.fix_wall[1]
                        c = self.fix_wall[2]
                        p1= self.fix_wall[3][0]
                        p2 = self.fix_wall[3][1]
                        x1= p1[0]
                        x2= p2[0]
                        y1_line = self.m *x1 + c
                        y2_line = self.m *x2 + c
                        p1_line = np.array([y1_line, x1])
                        p2_line = np.array([y2_line, x2])
                        origin = np.array([-0.45, 0])
                        v1 = p1_line - origin
                        v2 = p2_line - origin
                        dist1 = np.linalg.norm(v1)
                        dist2 = np.linalg.norm(v2)
                        if dist1 > dist2:
                            self.rotate_dir = -1.0
                            print("Hi")
                        elif dist1 == dist2: 
                            self.rotate_dir = -1.0 # default
                        else:
                            self.rotate_dir = +1.0
                            print("Hello")
                        
                        self.section_executed = True

                    m_new = self.fix_wall[1]
                    if self.flag == True and abs(m_new) >0.1:  #check for robile3 to parallel
                        msg4.angular.z = 0.1 * self.rotate_dir
                        self.cmd_vel_pub.publish(msg4)
                        return pt.common.Status.RUNNING
                    else:
                        print("parallel")
                        return pt.common.Status.FAILURE 
                   
                    

                                               
    def terminate(self, new_status):
        """
        terminate() is trigerred once the execution of the behavior finishes, 
        i.e. when the status changes from RUNNING to SUCCESS or FAILURE
        """
        self.logger.info("[ROTATE] terminate: publishing zero angular velocity")
        twist_msg = Twist()
        twist_msg.linear.x = 0.
        twist_msg.linear.y = 0.
        twist_msg.angular.z = 0.
                    
        self.cmd_vel_pub.publish(twist_msg)
        # print("aligned")
        self.blackboard.set('aligned',True)
        self.blackboard.set('wall_warn', False)
        self.slope = self.blackboard.get('slope')
        self.m1 = abs(self.slope)
        # self.wall_warn = self.blackboard.get('wall_warn')
        return pt.common.Status.RUNNING
        
        # # self.cmd_vel_pub.publish(twist_msg)
        # self.sent_goal = False
        # return super().terminate(new_status)              





class wall_following(pt.behaviour.Behaviour):

    """
    Move the robot about x-axis parallely to that wall with safe distance
    """

    def __init__(self, name="following_wall", topic_name="/cmd_vel", direction=1, max_ang_vel=0.5):

        self.topic_name = topic_name

        self.max_ang_vel = max_ang_vel # units: rad/sec

        self.direction = direction

        # Execution checker
        self.sent_goal = False

        # become a behaviour
        super(wall_following, self).__init__(name)

        self.blackboard = pt.blackboard.Blackboard()


        self.aligned = self.blackboard.get('aligned')
        self.distance = self.blackboard.get('near_distance')
        self.slope = self.blackboard.get('slope')
        self.dir_move = self.blackboard.get('wall')
        

        # self.res = self.blackboard.get('fix_wall')
    


        

    def setup(self, **kwargs):
        """
        Setting up things which generally might require time to prevent delay in tree initialisation
        """
        self.logger.info("[following_wall] setting up move_allign behavior")
        
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        # Create publisher to publish rotation commands
        self.cmd_vel_pub = self.node.create_publisher(
            msg_type=Twist,
            topic=self.topic_name,
            qos_profile=ptr.utilities.qos_profile_latched()
        )

        # self.distance = self.blackboard.get('near_distance')

        self.feedback_message = "setup"
        return True

    def update(self):
        """
        Primary function of the behavior is implemented in this method

        Rotating the robot at maximum allowed angular velocity in a given direction, 
        where, if **direction** is +1, it implies clockwise rotation, and if it is -1, it implies
        counter-clockwise rotation
        """
        self.logger.info("[following_wall] setting up move_allign behavior")
        self.logger.debug("%s.update()" % self.__class__.__name__)
        # self.d = self.blackboard.get('distance')
        self.distance = self.blackboard.get('near_distance')
        self.dir_move = self.blackboard.get('wall')
        # self.fix_wall = self.blackboard.get('fix_wall')
        self.slope = self.blackboard.get('slope')
        msg = Twist()
    
        if not self.blackboard.exists('laser_scan'):
            print("waiting")  # Laser data not available yet, keep waiting
            return pt.common.Status.RUNNING 
        else:
            print("Moving")
            self.fix_wall = self.blackboard.get('fix_wall')
            if self.fix_wall == [] or self.fix_wall == 'None':
                return pt.common.Status.FAILURE
            
            #need to write onmore if cond, if slope of fix wall is 0.0 and maintaing a safe range or not

            else:
                
                msg.linear.x = 0.1  #chnage the speed while working with robot
                msg.linear.y = 0.0
                msg.angular.z = 0.0

                self.cmd_vel_pub.publish(msg)
                return pt.common.Status.RUNNING 
            # else:
            #     return pt.common.Status.FAILURE 

               
            

            
                                
    def terminate(self, new_status):
        """
        terminate() is trigerred once the execution of the behavior finishes, 
        i.e. when the status changes from RUNNING to SUCCESS or FAILURE
        """
        self.logger.info("[ROTATE] terminate: publishing zero angular velocity")
        twist_msg = Twist()
        twist_msg.linear.x = 0.
        twist_msg.linear.y = 0.
        twist_msg.angular.z = 0.
                    
        self.cmd_vel_pub.publish(twist_msg)
        self.blackboard.set('aligned',False)
        self.blackboard.set('wall_warn',False)
        self.slope = self.blackboard.get('slope')
        self.m1 = abs(self.slope)
        
        return pt.common.Status.RUNNING                


            





