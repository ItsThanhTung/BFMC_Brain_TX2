import numpy as np
from math import cos, sin, tan
from libs import normalise_angle
class BicycleModel():
    def __init__(self, wheelbase: float, max_steer: float, delta_time: float=0.05):
        self.delta_time = delta_time
        self.wheelbase = wheelbase
        self.max_steer = max_steer

    def predict(self, CarState, SteeringAngle) -> tuple[float, ...]:
     
        """
        
        CarState["x"]   : x coordinate of Car (m)
        CarState["y"]   : y coordinate of Car (m)
        CarState["Velo"] : Velocity of Car (m/s)
        CarState["Heading"]: Car heading    (rad)

        Steering Angle: Current Steering Angle of Car
        
        """
        # Compute the local velocity in the x-axis
        newCarState = []
        newCarState["Velo"] = CarState["Velo"]

        # Limit steering angle to physical vehicle limits
        steering_angle = -self.max_steer if steering_angle < -self.max_steer else self.max_steer if steering_angle > self.max_steer else SteeringAngle
        beta = np.arctan(np.tan(steering_angle)/self.wheelbase)

        # Compute the final state using the discrete time model
        newCarState["x"]   = CarState["x"] + CarState["Velo"]*cos(CarState["Heading"] + beta)*self.delta_time
        newCarState["y"]   = CarState["y"] + CarState["Velo"]*sin(CarState["Heading"] + beta)*self.delta_time
        newCarState["Heading"] = CarState["Heading"] + CarState["Velo"]*np.tan(steering_angle)*np.cos(beta)/self.wheelbase
        
        return newCarState