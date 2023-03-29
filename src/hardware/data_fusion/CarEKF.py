from filterpy.kalman import ExtendedKalmanFilter as EKF
import numpy as np
import sympy
from sympy import Matrix
from sympy.abc import alpha, x, y, V, R, theta, beta, a, L
from src.utils.CarModel.BicycleModel import BicycleModel


x_var = 3
y_var = 3
Vel_var = 3
Heading_var = 2

Enc_Vel_Var = 2

GPS_x_Var = 5
GPS_y_Var = 5

IMU_Velo_Var = 2
IMU_Heading_Var = 2

class CarEKF(EKF):
    def __init__(self, delta_t, WheelBase, maxSteer):
        EKF.__init__(self, 4,2,2)
        self._dt = delta_t

        dt = sympy.symbols("delta_t")
        self.stateMat = Matrix([[x],[y], [V], [theta]])

        self.inputMat = Matrix([[V], [alpha]])
        self.fxu =  Matrix([[x + dt*V*sympy.cos(theta + beta)],
                            [y + dt*V*sympy.sin(theta + beta)],
                            [V + a* dt ],
                            [theta + dt*V*sympy.tan(alpha)*sympy.cos(beta)/L]
                            ])
        self.subs ={
            x:0, y:0, V:0, theta:0,
            dt: delta_t, L: WheelBase,
            alpha: 0
        }
        self.PredictCov = np.array([x_var**2, 0, 0, 0],
                                   [0, y_var**2, 0, 0],
                                   [0, 0, Vel_var**2, 0],
                                   [0, 0, 0, Heading_var**2])
        self.F_jac = self.fxu.jacobian(self.stateMat)
        self.V_jac = self.fxu.jacobian(self.inputMat)


    
    def predict(self, u):
        self.subs[x] = self.x[0,0]
        self.subs[y] = self.x[1,0]
        self.subs[theta] = self.x[3,0]

        self.subs[V] = u["Velo"]
        self.subs[alpha] = u["Angle"]
        self.x = np.array(self.fxu.evalf(subs= self.subs), dtype = float)
        F =  np.array(self.F_jac.evalf(subs = self.subs), dtype=float)
        V = np.array(self.V_jac.evalf(subs = self.subs), dtype=float)

        self.x[3,0] = self.wrapAngle(self.x[3,0])
    
        self.P = F @ self.P @ F.T + V @ self.PredictCov @ V.T

    def residual(self, a, b):
        y = a-b
        y[3] = self.wrapAngle(y[3]) 
    
    def wrapAngle(self,Angle):
        Angle = Angle % (2 * np.pi)    # force in range [0, 2 pi)
        if Angle > np.pi:             # move to [-pi, pi)
            Angle -= 2 * np.pi
        

    def _Encoder_hx(self,x):
        return np.array([x[2,0]]) 
    
    def _Encoder_H_j(self, x):
        return np.array([0, 0, 1, 0])

    def Encoder_Update(self, Velocity):
        EncNoiseMat = [Enc_Vel_Var**2]
        z = np.array([[Velocity]])
        self.update(z,self._Encoder_H_j, self._Encoder_hx, EncNoiseMat,residual= self.residual)

    def _GPS_hx(self, x):
        return np.array([[x[0,0], y[1,0]]])
    
    def _GPS_H_j(self, x):
        return np.array([[1,0,0,0],
                         [0,1,0,0]])
    
    def GPS_Update(self, x, y):
        GPS_NoiseMat = np.array([[GPS_x_Var**2, 0],
                                 [0, GPS_y_Var**2]])
        z = np.array([[x], [y]])
        self.update(z, self._GPS_H_j, self._GPS_hx, GPS_NoiseMat, residual= self.residual)

    def _IMU_hx(self, x):
        return np.array([[x[2:0]],
                         [x[3:0]]])
    
    def _IMU_H_j(self, x):
        return np.array([[0, 0, 1, 0],
                         [0, 0, 0, 1]])
    
    def IMU_Update(self, Velocity, heading):
        IMU_NoiseMat = np.array([[IMU_Velo_Var**2, 0],
                                 [0, IMU_Heading_Var**2]])
        z = np.array([[Velocity], [heading]])
        self.update(z, self._IMU_H_j, self._IMU_hx, IMU_NoiseMat, residual= self.residual)
    
    def GetCarState(self):
        return{
            "x": self.x[0,0],
            "y": self.x[1,0],
            "Velo": self.x[2,0],
            "Heading":self.x[3,0]
        }







    