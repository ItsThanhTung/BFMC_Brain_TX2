from filterpy.kalman import ExtendedKalmanFilter as EKF
import numpy as np
import sympy
from sympy import Matrix
from sympy.abc import alpha, x, y, V, R, theta, beta, a, L
from src.utils.CarModel.BicycleModel import BicycleModel


Enc_Vel_std = 1

GPS_x_std = 1
GPS_y_std = 1

IMU_Velo_std = 2
IMU_Heading_std = 0.05

inVel_std = 1
inSteer_std = 1 

class CarEKF(EKF):
    def __init__(self, delta_t, WheelBase):
        EKF.__init__(self, 4,2,2)
        self._dt = delta_t

        dt = sympy.symbols("delta_t")
        self.stateMat = Matrix([[x],[y], [V], [theta]])
        beta = sympy.atan((WheelBase/2) * sympy.tan(alpha)/WheelBase)
        self.inputMat = Matrix([[V], [alpha]])
        self.fxu =  Matrix([[x + dt*V*sympy.cos(theta + beta)],
                            [y + dt*V*sympy.sin(theta + beta)],
                            [V],
                            [theta + dt*V*sympy.tan(alpha)*sympy.cos(beta)/WheelBase]
                            ])
        self.subs ={
            x:0, y:0, V:0, theta:0,
            dt: delta_t, L: WheelBase,
            alpha: 0
        }

        self.PredictCov = np.array([[inVel_std**2, 0],
                                    [0, inSteer_std**2]])
        self.F_jac = self.fxu.jacobian(self.stateMat)
        self.V_jac = self.fxu.jacobian(self.inputMat)

    def InitialState(self, X, Y, Velo, Heading):
        self.x[0,0] = X
        self.x[1,0] = Y
        self.x[2,0] = Velo
        self.x[3,0] = Heading
    
    def predict(self, u):
        self.subs[x] = self.x[0,0]
        self.subs[y] = self.x[1,0]
        self.subs[theta] = self.x[3,0]
        # print("subs ", self.subs)

        self.subs[V] = u["Velo"]
        self.subs[alpha] = u["Angle"]
        self.x = np.array(self.fxu.evalf(subs= self.subs), dtype = float)
        F =  np.array(self.F_jac.evalf(subs = self.subs), dtype = float)
        H = np.array(self.V_jac.evalf(subs = self.subs), dtype = float)

        self.x[3,0] = self.wrapAngle(self.x[3,0])

        self.P = F @ self.P @ F.T + H @ self.PredictCov @ H.T

        self.x_prior = self.x.copy()
        self.P_prior = self.P.copy()

    def IMUResidual(self, a, b):
        y = a-b
        y[1] = self.wrapAngle(y[1])
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
        EncNoiseMat = np.array([[Enc_Vel_std**2]])
        z = np.array([[Velocity]])
        self.update(z,self._Encoder_H_j, self._Encoder_hx, EncNoiseMat)


    def _IMU_hx(self, x):
        return np.array([[x[2,0]],
                         [x[3,0]]])
        # return np.array([[x[3,0]]])
    
    def _IMU_H_j(self, x):
        # return np.array([[0, 0, 0, 1]])
        return np.array([[0, 0, 1, 0],
                        [0, 0, 0, 1]])
    
    def IMU_Update(self, Velocity, heading):
        IMU_NoiseMat = np.array([[IMU_Velo_std**2, 0],
                                 [0, IMU_Heading_std**2]])
        z = np.array([[Velocity], [heading]])
        self.update(z, self._IMU_H_j, self._IMU_hx, IMU_NoiseMat, residual= self.IMUResidual)
        # IMU_NoiseMat = np.array([[IMU_Heading_std**2]])
        # z = np.array([[heading]])
        # self.update(z, self._IMU_H_j, self._IMU_hx, IMU_NoiseMat, residual= self.IMUResidual)
    def _GPS_hx(self, x):
        return np.array([[x[0,0]], 
                          [x[1,0]]])
    
    def _GPS_H_j(self, x):
        return np.array([[1,0,0,0],
                         [0,1,0,0]])
    
    def GPS_Update(self, x, y):
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







    