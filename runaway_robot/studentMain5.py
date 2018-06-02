# ----------
# Part Five
#
# This time, the sensor measurements from the runaway Traxbot will be VERY
# noisy (about twice the target's stepsize). You will use this noisy stream
# of measurements to localize and catch the target.
#
# ----------
# YOUR JOB
#
# Complete the next_move function, similar to how you did last time.
#
# ----------
# GRADING
#
# Same as part 3 and 4. Again, try to catch the target in as few steps as possible.

from robot import *
from math import *
import random
import numpy as np
from numpy import linalg, array, empty, newaxis, r_, emath
# from numpy import *
from matrix import *
from scipy import optimize, odr


class KFilter:
    def __init__(self):

        self.a = matrix([[0.], [0.]]) # external motion
        self.F =  matrix([[1.0, 0.0], [0.0, 1.0]])
        self.H =  matrix([[1.0, 0.0], [0.0, 1.0]])
        self.R =  matrix([[0.1, 0.0], [0.0, 0.1]])
        self.I =  matrix([[1.0, 0.0], [0.0, 1.0]])
      
    def filter(self, measurements, x, P):  
        for n in range(len(measurements)):
            # prediction
            x = (self.F * x) + self.a
            P = self.F * P * self.F.transpose()
    
            # measurement update
            Z = matrix([measurements[n]])
            y = Z.transpose() - (self.H * x)
            S = self.H * P * self.H.transpose() + self.R
            K = P * self.H.transpose() * S.inverse()
            x = x + (K * y)
            P = (self.I - (K * self.H)) * P
        return x, P

   # the belowing circle radius, center calculation was referenced from http://scipy-cookbook.readthedocs.io/items/Least_Squares_Circle.html
    # different methods used to find the least squares circle fitting a set of 2D points (x,y).
# class Circle_3b:
#
#     def __init__(self, x1, y1):
#         self.x1 = x1
#         self.y1 = y1
#         self.x = [x1, y1]
#
#     def calc_R(self, xc, yc):
#         """ calculate the distance of each 2D points from the center (xc, yc) """
#         return sqrt((self.x1-xc)**2 + (self.y1-yc)**2)
#
#
#     def f_3b(self, beta, x):
#         """ implicit definition of the circle """
#         return (x[0]-beta[0])**2 + (x[1]-beta[1])**2 -beta[2]**2
#
#     def jacb(self, beta, x):
#         """ Jacobian function with respect to the parameters beta.
#         return df_3b/dbeta
#         """
#         xc, yc, r = beta
#         xi, yi    = x
#
#         df_db    = empty((beta.size, x.shape[1]))
#         df_db[0] =  2*(xc-xi)                     # d_f/dxc
#         df_db[1] =  2*(yc-yi)                     # d_f/dyc
#         df_db[2] = -2*r                           # d_f/dr
#
#         return df_db
#
#     def jacd(self, beta, x):
#         """ Jacobian function with respect to the input x.
#         return df_3b/dx
#         """
#         xc, yc, r = beta
#         xi, yi    = x
#
#         df_dx    = empty_like(x)
#         df_dx[0] =  2*(xi-xc)                     # d_f/dxi
#         df_dx[1] =  2*(yi-yc)                     # d_f/dyi
#
#         return df_dx
#
#     def calc_estimate(self, data):
#         """ Return a first estimation on the parameter from the data  """
#         xc0, yc0 = data.x.mean(axis=1)
#         r0 = sqrt((data.x[0]-xc0)**2 +(data.x[1] -yc0)**2).mean()
#         return xc0, yc0, r0
#
#     # for implicit function :
#     #       data.x contains both coordinates of the points
#     #       data.y is the dimensionality of the response
#     def implement(self):
#         lsc_data  = odr.Data(row_stack([self.x1, self.y1]), y=1)
#         lsc_model = odr.Model(self.f_3b, implicit=True, estimate=self.calc_estimate, fjacd=self.jacd, fjacb=self.jacb)
#         lsc_odr   = odr.ODR(lsc_data, lsc_model)    # beta0 has been replaced by an estimate function
#         lsc_odr.set_job(deriv=3)                    # use user derivatives function without checking
#         # lsc_odr.set_iprint(iter=1, iter_step=1)     # print details for each iteration
#         lsc_out   = lsc_odr.run()
#         xc_3b, yc_3b, Radius = lsc_out.beta
#         Ri_3b       = self.calc_R(xc_3b, yc_3b)
#         residu   = sum((Ri_3b - Radius)**2)
#         dce = [xc_3b, yc_3b]
#         return dce, Radius, residu
#
#
# class Circle_3:
#     def __init__(self, x1, y1):
#         self.x1 = x1
#         self.y1 = y1
#         self.x = [x1, y1]
#
#     def calc_R(self, xc, yc):
#         """ calculate the distance of each 2D points from the center (xc, yc) """
#         return sqrt((self.x1-xc)**2 + (self.y1-yc)**2)
#
#     def f_3(self, beta, x):
#         """ implicit definition of the circle """
#         return (x[0]-beta[0])**2 + (x[1]-beta[1])**2 -beta[2]**2
#
#     def implement(self):
#         _x_ = mean(self.x1)
#         _y_ = mean(self.y1)
#         # initial guess for parameters
#         R_m = self.calc_R(_x_, _y_).mean()
#         beta0 = [ _x_, _y_, R_m]
#
#         # for implicit function :
#         #       data.x contains both coordinates of the points (data.x = [x, y])
#         #       data.y is the dimensionality of the response
#         lsc_data  = odr.Data(row_stack([self.x1, self.y1]), y=1)
#         lsc_model = odr.Model(self.f_3, implicit=True)
#         lsc_odr   = odr.ODR(lsc_data, lsc_model, beta0)
#         lsc_out   = lsc_odr.run()
#
#         xc_3, yc_3, R_3 = lsc_out.beta
#         Ri_3 = self.calc_R(xc_3, yc_3)
#         residu = sum((Ri_3 - R_3)**2)
#         dce = [xc_3, yc_3]
#         Radius = R_3
#         return dce, Radius, residu
#
# class Circle_2:
#     def __init__(self, x1, y1):
#         self.x1 = x1
#         self.y1 = y1
#         self.x = [x1, y1]
#
#     def calc_R(self, xc, yc):
#         """ calculate the distance of each 2D points from the center (xc, yc) """
#         return sqrt((self.x1-xc)**2 + (self.y1-yc)**2)
#
#     def f_2(self, c):
#         """ calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc) """
#         Ri = self.calc_R(*c)
#         return Ri - Ri.mean()
#
#     def implement(self):
#         _x_ = mean(self.x1)
#         _y_ = mean(self.y1)
#         center_estimate = _x_, _y_
#         center_2, ier = optimize.leastsq(self.f_2, center_estimate)
#
#         xc_2, yc_2 = center_2
#         dce = [xc_2, yc_2]
#         Ri_2       = self.calc_R(*center_2)
#         R_2        = Ri_2.mean()
#         residu_2   = sum((Ri_2 - R_2)**2)
#         return dce, R_2, residu_2
#
# class Circle_2b:
#     def __init__(self, x1, y1):
#         self.x1 = x1
#         self.y1 = y1
#         self.x = [x1, y1]
#
#     def calc_R(self, xc, yc):
#         """ calculate the distance of each 2D points from the center (xc, yc) """
#         return sqrt((self.x1-xc)**2 + (self.y1-yc)**2)
#
#     def f_2b(self, c):
#         """ calculate the algebraic distance between the 2D points and the mean circle centered at c=(xc, yc) """
#         Ri = self.calc_R(*c)
#         return Ri - Ri.mean()
#
#     def Df_2b(self, c):
#         """ Jacobian of f_2b
#         The axis corresponding to derivatives must be coherent with the col_deriv option of leastsq"""
#         xc, yc     = c
#         df2b_dc    = empty((len(c), self.x1.size))
#         Ri = self.calc_R(xc, yc)
#         df2b_dc[0] = (xc - self.x1)/Ri                   # dR/dxc
#         df2b_dc[1] = (yc - self.y1)/Ri                   # dR/dyc
#         df2b_dc    = df2b_dc - df2b_dc.mean(axis=1)[:, newaxis]
#         return df2b_dc
#
#     def implement(self):
#         _x_ = mean(self.x1)
#         _y_ = mean(self.y1)
#
#         center_estimate = _x_, _y_
#         center_2b, ier = optimize.leastsq(self.f_2b, center_estimate, Dfun=self.Df_2b, col_deriv=True)
#         # print "center_2b", center_2b
#
#         xc_2b, yc_2b = center_2b
#         Ri_2b        = self.calc_R(*center_2b)
#         R_2b         = Ri_2b.mean()
#         residu_2b    = sum((Ri_2b - R_2b)**2)
#
#         dce = [xc_2b, yc_2b]
#         Radius = R_2b
#         return dce, Radius, residu_2b

class Circle_1:
    def __init__(self, xs, ys):
        self.xs = xs
        self.ys = ys

    def calc_R(self, xc, yc):
        """ calculate the distance of each 2D points from the center (xc, yc) """
        return sqrt((self.x1-xc)**2 + (self.y1-yc)**2)

    def implement(self):
        _x_ = sum(self.xs) / len(self.xs)
        _y_ = sum(self.ys) / len(self.ys)
        a, b = [], []
        for i in range(len(self.xs)):
            a.append(self.xs[i] - _x_)
            b.append(self.ys[i] - _y_)
        dic = {"a":a,"b":b}
        ab, aa, bb, aab, abb, aaa, bbb = [], [], [], [], [], [], []
        itemlist = ['ab', 'aa', 'bb', 'aab', 'abb', 'aaa', 'bbb']
        varlist = [ab, aa, bb, aab, abb, aaa, bbb]
        for k in range(len(itemlist)):
            t1 = list(itemlist[k])
            for i in range(len(self.xs)):
                x = 1
                for key in t1:
                    x *= dic[key][i]
                # exec "%s.append(%s)" % (itemlist[k], x)
                varlist[k].append(x)
        M = matrix([[sum(aa), sum(ab)], [sum(ab), sum(bb)]]).inverse() * matrix([[sum(aaa) + sum(abb)], [sum(bbb) + sum(aab)]])
        dce = [sum(self.xs) / len(self.xs) + M.value[0][0] / 2.0, sum(self.ys) / len(self.ys) + M.value[1][0] / 2.0]
        return dce


def next_move(hunter_position, hunter_heading, target_measurement, max_distance, OTHER = None):
    # This function will be called after each time the target moves.

    # The OTHER variable is a place for you to store any historical information about
    # the progress of the hunt (or maybe some localization information). Your return format
    # must be as follows in order to be graded properly.
    if not OTHER: # first time calling this function, set up my OTHER variables.
        measurements = []
        hunter_positions = []
        hunter_headings = []
        xs = []
        ys = []
        P = matrix([[1000.0, 0.0], [0.0, 1000.0]])
        OTHER = [measurements, hunter_positions, hunter_headings, xs, ys, P] # now I can keep track of history
    else: # not the first time, update my history
        measurements, hunter_positions, hunter_headings, xs, ys, P = OTHER # now I can always refer to these variables

    measurements.append(target_measurement)
    hunter_positions.append(hunter_position)
    hunter_headings.append(hunter_heading)

    #apply kfilter to decrease noise
    #code to use the original kfilter
    # x = matrix([[target_measurement[0]], [target_measurement[1]]]) # initial state (location and velocity)
    # kfilter = KFilter()
    # x, P = kfilter.filter(measurements[-30:], x, P)
    # fx = x.value[0][0]
    # fy = x.value[1][0]
    # xy = (fx, fy)

    # the algorithm was referenced from http://scipy-cookbook.readthedocs.io/items/Least_Squares_Circle.html
    # different methods used to find the least squares circle fitting a set of 2D points (x,y).
    if len(xs) < 5:
        xs.append(target_measurement[0])
        ys.append(target_measurement[1])
        pred_position  = target_measurement
    else:
        xs.append(target_measurement[0])
        ys.append(target_measurement[1])

        circle = Circle_1(xs, ys)
        dce = circle.implement()

        cir, beta, degree = [], [], []
        m_beta, m_degree = 0, 0
        for i in range(len(xs)):
            beta.append(atan2(ys[i] - dce[1], xs[i] - dce[0]))
            degree.append(degrees(beta[i]))
            m_beta = m_beta + (angle_trunc(beta[i] - beta[i - 1]) if i > 0 else 0)
            cir.append(sqrt((xs[i]-dce[0])**2 + (ys[i]-dce[1])**2))
        m_beta /= (len(beta) - 1)
        Radius = sum(cir) / len(cir)
        m_degree = degrees(m_beta)

        s_beta = 0
        count = 5
        left = count - len(OTHER[0]) % count - 1
        for i in range(len(xs)):
            s_beta = s_beta + ((beta[i] - m_beta * i) % pi - (0 if beta[0] >= 0 else pi))
        s_beta = s_beta/len(beta)
        n_beta = (len(beta) + left) * m_beta + s_beta
        pred_position  = (dce[0] + Radius * cos(n_beta), dce[1] + Radius * sin(n_beta))

    OTHER[0] = measurements
    OTHER[1] = hunter_positions
    OTHER[2] = hunter_headings
    OTHER[3] = xs
    OTHER[4] = ys
    OTHER[5] = P

    heading_to_target = get_heading(hunter_position, pred_position)
    turning = angle_trunc(heading_to_target - hunter_heading)
    distance = sqrt((pred_position [0] - hunter_position[0])**2 + (pred_position [1] - hunter_position[1])**2)
    return turning, distance, OTHER

def distance_between(point1, point2):
    """Computes distance between point1 and point2. Points are (x, y) pairs."""
    x1, y1 = point1
    x2, y2 = point2
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def demo_grading(hunter_bot, target_bot, next_move_fcn, OTHER = None):
    """Returns True if your next_move_fcn successfully guides the hunter_bot
    to the target_bot. This function is here to help you understand how we
    will grade your submission."""
    max_distance = 0.97 * target_bot.distance # 0.97 is an example. It will change.
    separation_tolerance = 0.02 * target_bot.distance # hunter must be within 0.02 step size to catch target
    caught = False
    ctr = 0

    # We will use your next_move_fcn until we catch the target or time expires.
    while not caught and ctr < 1000:

        # Check to see if the hunter has caught the target.
        hunter_position = (hunter_bot.x, hunter_bot.y)
        target_position = (target_bot.x, target_bot.y)
        separation = distance_between(hunter_position, target_position)
        if separation < separation_tolerance:
            print "You got it right! It took you ", ctr, " steps to catch the target."
            caught = True

        # The target broadcasts its noisy measurement
        target_measurement = target_bot.sense()

        # This is where YOUR function will be called.
        turning, distance, OTHER = next_move_fcn(hunter_position, hunter_bot.heading, target_measurement, max_distance, OTHER)

        # Don't try to move faster than allowed!
        if distance > max_distance:
            distance = max_distance

        # We move the hunter according to your instructions
        hunter_bot.move(turning, distance)

        # The target continues its (nearly) circular motion.
        target_bot.move_in_circle()

        ctr += 1
        if ctr >= 1000:
            print "It took too many steps to catch the target."
    return caught



def angle_trunc(a):
    """This maps all angles to a domain of [-pi, pi]"""
    while a < 0.0:
        a += pi * 2
    return ((a + pi) % (pi * 2)) - pi

def get_heading(hunter_position, target_position):
    """Returns the angle, in radians, between the target and hunter positions"""
    hunter_x, hunter_y = hunter_position
    target_x, target_y = target_position
    heading = atan2(target_y - hunter_y, target_x - hunter_x)
    heading = angle_trunc(heading)
    return heading

def naive_next_move(hunter_position, hunter_heading, target_measurement, max_distance, OTHER):
    """This strategy always tries to steer the hunter directly towards where the target last
    said it was and then moves forwards at full speed. This strategy also keeps track of all
    the target measurements, hunter positions, and hunter headings over time, but it doesn't
    do anything with that information."""
    if not OTHER: # first time calling this function, set up my OTHER variables.
        measurements = [target_measurement]
        hunter_positions = [hunter_position]
        hunter_headings = [hunter_heading]
        OTHER = (measurements, hunter_positions, hunter_headings) # now I can keep track of history
    else: # not the first time, update my history
        OTHER[0].append(target_measurement)
        OTHER[1].append(hunter_position)
        OTHER[2].append(hunter_heading)
        measurements, hunter_positions, hunter_headings = OTHER # now I can always refer to these variables

    heading_to_target = get_heading(hunter_position, target_measurement)
    heading_difference = heading_to_target - hunter_heading
    turning =  heading_difference # turn towards the target
    distance = max_distance # full speed ahead!
    return turning, distance, OTHER

# target = robot(0.0, 10.0, 0.0, 2*pi / 30, 1.5)
# measurement_noise = 2.0*target.distance # VERY NOISY!!
# target.set_noise(0.0, 0.0, measurement_noise)
#
# hunter = robot(-10.0, -10.0, 0.0)

# print demo_grading(hunter, target, next_move)



