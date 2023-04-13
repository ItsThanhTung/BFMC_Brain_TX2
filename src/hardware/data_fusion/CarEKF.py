from filterpy.kalman import ExtendedKalmanFilter as EKF
import numpy as np
# import sympy
# from sympy import Matrix
# from sympy.abc import alpha, x, y, V, R, theta, beta, a, L
# from src.utils.CarModel.BicycleModel import BicycleModel


Enc_Vel_std = 0.5


GPS_x_std = 0.7
GPS_y_std = 0.7

IMU_Velo_std = 1
IMU_Heading_std = 0.1

inVel_std = 0.5
inSteer_std = 0.5 

class CarEKF(EKF):
    def __init__(self, delta_t, WheelBase):
        EKF.__init__(self, 4,2,2)
        self._dt = delta_t
        self._WheelBase = WheelBase
        
        self.isIntial = False
        self.PredictCov = np.array([[inVel_std**2, 0],
                                    [0, inSteer_std**2]])


    def InitialState(self, X, Y, Velo, Heading):
        self.x[0,0] = X
        self.x[1,0] = Y
        self.x[2,0] = Velo
        self.x[3,0] = Heading
        # self.P = np.array([[0.3**2, 0, 0, 0],
        #                    [0, 0.3**2, 0, 0],
        #                    [0, 0, 0.5**2, 0],
        #                    [0, 0, 0, 0.2**2]])
        self.isIntial = True
    
    def predict(self, u, dt):

        _x, _y, _theta = self.x[0,0], self.x[1,0], self.x[3,0]
        # _Velo = self.x[2,0]
        # _Velo, _alpha = u["Velo"], u["Angle"]
        _Velo, _alpha = u["Velo"], u["Angle"]

        _dt = dt
        _wheelbase = self._WheelBase

        _beta = np.arctan(np.tan(_alpha)/2)
        self.x[0,0] = _x + _Velo*_dt*np.cos(_theta + _beta)
        self.x[1,0] = _y +  _Velo*_dt*np.sin(_theta + _beta)
        self.x[2,0] = _Velo
        self.x[3,0] = _theta + _Velo*_dt*np.tan(_alpha)*np.cos(_beta)/_wheelbase


        F = np.array([[1, 0, _dt*np.cos(_beta+_theta), -_Velo*_dt*np.sin(_beta+_theta)],
                      [0, 1, _dt*np.sin(_beta+_theta), _Velo*_dt*np.cos(_beta+_theta)],
                      [0,0,1,0],
                      [0,0, _dt*np.cos(_beta)*np.tan(_alpha)/ _wheelbase, 1]
                      ], dtype = float)

        H = np.array([[ _dt* np.cos(_beta + _theta), 0],
                      [ _dt * np.sin(_beta + _theta), 0],
                      [1, 0],
                      [ _dt*np.cos(_beta)*np.tan(_alpha)/_wheelbase, _Velo*_dt*((np.tan(_alpha)**2) + 1)*np.cos(_beta)/_wheelbase]],
                      dtype=float)

        self.x[3,0] = self.wrapAngle(self.x[3,0])

        self.P = F @ self.P @ F.T + H @ self.PredictCov @ H.T

        self.x_prior = self.x.copy()
        self.P_prior = self.P.copy()

    def IMUResidual(self, a, b):
        y = a-b
        y[0] = self.wrapAngle(y[0])
        return y
    
    def wrapAngle(self,Angle):
        Angle = Angle % (2 * np.pi)    # force in range [0, 2 pi)
        if Angle > np.pi:             # move to [-pi, pi)
            Angle -= 2 * np.pi
        return Angle

    def _Encoder_hx(self,x):
        return np.array([[x[2,0]]]) 
    
    def _Encoder_H_j(self, x):
        return np.array([[0, 0, 1, 0]])

    def Encoder_Update(self, Velocity):
        if not self.isIntial:
            return
        EncNoiseMat = np.array([[Enc_Vel_std**2]])
        z = np.array([[Velocity]])
        self.update(z,self._Encoder_H_j, self._Encoder_hx, EncNoiseMat)


    def _IMU_hx(self, x):
        # return np.array([[x[2,0]],
        #                  [x[3,0]]])
        return np.array([[x[3,0]]])
    
    def _IMU_H_j(self, x):
        return np.array([[0, 0, 0, 1]])
        # return np.array([[0, 0, 1, 0],
        #                 [0, 0, 0, 1]])
    
    def IMU_Update(self, heading):
        if not self.isIntial:
            return
        # IMU_NoiseMat = np.array([[IMU_Velo_std**2, 0],
        #                          [0, IMU_Heading_std**2]])
        # z = np.array([[Velocity], [heading]])
        # self.update(z, self._IMU_H_j, self._IMU_hx, IMU_NoiseMat, residual= self.IMUResidual)
        IMU_NoiseMat = np.array([[IMU_Heading_std**2]])
        z = np.array([[heading]])
        self.update(z, self._IMU_H_j, self._IMU_hx, IMU_NoiseMat, residual= self.IMUResidual)
    def _GPS_hx(self, x):
        return np.array([[x[0,0]], 
                          [x[1,0]]])
    
    def _GPS_H_j(self, x):
        return np.array([[1,0,0,0],
                         [0,1,0,0]])
    
    def GPS_Update(self, x, y):
        if not self.isIntial:
            return
        Velo = self.x[2,0]
        GPS_x_std = (Velo+0.15)**2
        GPS_y_std = (Velo+0.15)**2
        GPS_NoiseMat = np.array([[GPS_x_std**2, 0],
                                 [0, GPS_y_std**2]])
        z = np.array([[x], [y]])
        self.update(z, self._GPS_H_j, self._GPS_hx, GPS_NoiseMat)

    def GetCarState(self):
        return{
            "x": self.x[0,0],
            "y": self.x[1,0],
            "Velo": self.x[2,0],
            "Heading":self.x[3,0]
        }

