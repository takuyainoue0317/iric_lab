# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 16:13:50 2019

@author: river801
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# set workiing directly and file name

path    = "C:/Users/river801/Dropbox/temp/WRR/"
fname   = "qr-t"

# read data: Time(h), Discharge(m3/s), Precipitation(mm/h)

with open(path+fname+".txt","r") as fpin:
    lines = fpin.readlines()
    tt = []
    qq = []
    rr = []
    for line in lines:
        value = line.replace('\n', '').split('\t')
        tt.append(float(value[0]))
        qq.append(float(value[1]))
        rr.append(float(value[2]))
    
fpin.close()

nt = len(tt)-1
tuk   = 200.
etime = tt[nt]*3600.


# Setting the river geometry and model parameters

g = 9.81

chlen  = 100*1000       # length of river reach (m)
wid    = 200            # channel width (m)
snm    = 0.03           # mannings roughness coefs
ib     = 1.0/2000.0      # bed slope

nx = 100    # number of grid
dx = chlen/float(nx)    # size of grid
dt = 0.2    # computational time step (sec)

x   = np.zeros(nx+1)
h   = np.zeros(nx+1)
u   = np.zeros(nx+1)
wu  = np.zeros(nx+1)
q   = np.zeros(nx+1)

x[0] = 0.

for i in np.arange(1,nx+1):
    x[i] = x[i-1]+dx
    
q0 = qq[0]
h0 = (snm*q0/(wid*ib**0.5))**0.6

for i in np.arange(nx+1):
    h[i]  = h0
    u[i]  = q0/(h0*wid)
    q[i]  = q0/wid

time = 0.
optime = 0.

t_cal = []
q_obs = []
q_cal = []
    
while time<etime:
    nn = int(time/3600)
    
    q0 = qq[nn]+(qq[nn+1]-qq[nn])/3600.*(time-nn*3600.)
    h0 = (snm*q0/(wid*ib**0.5))**0.6
    
    u[0] = q0/(h[0]*wid)
    q[0] = q0/wid
    
    for i in np.arange(1,nx):
        h_bar = (h[i]+h[i+1])*0.5
        pressure = -g*(-h[i]+h[i+1])/dx+g*ib
        roughness = g*snm**2.0*u[i]/h_bar**(4.0/3.0)
        advection = u[i]*(-u[i-1]+u[i])/dx
        wu[i] = (u[i]+(-advection+pressure)*dt)/(1.0+roughness*dt)
        q[i] = wu[i]*h_bar
            
    wu[nx] = wu[nx-1]
    q[nx] = q[nx-1]
    
    for i in np.arange(1,nx):
        h[i] = h[i]-(-q[i-1]+q[i])/dx*dt
        
    h[nx] = h[nx-1]
    
    for i in np.arange(1,nx+1):
        u[i] = wu[i]
    
    if optime>tuk:
        print(time/3600,q0,q[nx]*wid)
        t_cal.append(time/3600.)
        q_obs.append(q0)
        q_cal.append(q[nx]*wid)
        optime = optime-tuk
    
    optime+=dt
    time+=dt
    
plt.plot(t_cal,q_obs,color='k', label="Given hydrograph")
plt.plot(t_cal,q_cal,color='b', label="Downstream end")

plt.xlabel( "Time (h)" )
plt.ylabel( "Discharge (m$^3$/s)" )
#plt.set.xlim([0,72])
#plt.set.ylim([0,3000])

plt.legend()

plt.savefig(path+fname+"-dynamic.jpg",dpi=300)
plt.close()

