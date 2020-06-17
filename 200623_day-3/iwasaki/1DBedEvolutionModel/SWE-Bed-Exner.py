# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 16:13:50 2019

@author: river801
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# set workiing directly and file name

tuk   = 600.
etime = tuk*3600.

# Setting the river geometry and model parameters

g = 9.81
nu = 0.000001

dis    = 200.
chlen  = 2000       # length of river reach (m)
wid    = 200            # channel width (m)
snm    = 0.03           # mannings roughness coefs
ib     = 0.002      # bed slope
ib2    = 0.01
spec   = 1.65
diam   = 0.002
tsc    = 0.05
poro   = 0.4
hdown  = 3.

nx = 100    # number of grid
dx = chlen/float(nx)    # size of grid
dt = 0.2    # computational time step (sec)

x   = np.zeros(nx+1)
z   = np.zeros(nx+1)
h   = np.zeros(nx+1)
u   = np.zeros(nx+1)
wu  = np.zeros(nx+1)
q   = np.zeros(nx+1)
hh  = np.zeros(nx+1)
xc  = np.zeros(nx+1)
eta = np.zeros(nx+1)
qb  = np.zeros(nx+1)

x[0] = 0.

for i in np.arange(1,nx+1):
    x[i] = x[i-1]+dx
    

z00  = chlen*ib*0.75 + chlen*ib2*0.25
z[0] = z00

for i in np.arange(1,nx+1):
    if i<0.3*nx or 0.4*nx<i<0.6*nx or i>0.7*nx:
        z[i] = z[i-1]-ib*dx
    else:
        z[i] = z[i-1]-ib2*dx
    
#for i in np.arange(1,nx+1):
#    if 0.45*nx < i < 0.55*nx:
##        z[i] = z[i] + 0.3*h0
        
for i in np.arange(1,nx+1):
    eta[i] = (z[i-1]+z[i])*0.5
    xc[i] = (x[i-1]+x[i])*0.5
    
h0 = (snm*dis/(wid*ib**0.5))**0.6

for i in np.arange(1,nx+1):
    h[i]  = h0
    u[i]  = dis/(h0*wid)
    q[i]  = dis/wid
        
h[0] = h0
u[0]  = dis/(h0*wid)
q[0]  = dis/wid

time = 0.
optime = 0.

n = 0
    
while time<etime:
    
    h0 = (snm*dis/(wid*ib**0.5))**0.6
    
    u[0] = dis/(h[0]*wid)
    q[0] = dis/wid
    
    for i in np.arange(1,nx):
        h_bar = (h[i]+h[i+1])*0.5
        pressure = -g*(-h[i]+h[i+1])/dx-g*(-eta[i]+eta[i+1])/dx
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
        
    for i in np.arange(1,nx):
        h_bar = (h[i]+h[i+1])*0.5
        ts = (snm*u[i])**2./(spec*diam*h_bar**(1./3.))
        if ts>tsc:
            qb[i] = 4.0*(ts-tsc)**1.5*(spec*g*diam**3.)**0.5
        else:
            qb[i] = 0.
        
    qb[ 0] = qb[1]
    qb[nx] = qb[nx-1]
    
    if time>1000:
    
        for i in np.arange(1,nx+1):
            eta[i] = eta[i]-(-qb[i-1]+qb[i])/dx*dt/(1.-poro)
    
    if optime>tuk:
        print("Time= ",time/3600)
        optime = optime-tuk
        
        hh = h+eta
        
        plt.xlim([0,chlen])
        plt.ylim([0,z00+h0*1.3])
        plt.plot(xc[1:nx],eta[1:nx],color='k',label='Bed surface')
        plt.plot(xc[1:nx],hh[1:nx],color='b',label='Water surface')
        
        plt.xlabel( "Downstream distance (m)" ) 
        plt.ylabel( "Elevation (m)" )
        
        plt.legend()
        
        nnn = str(n)
        
        plt.savefig('Figure' + nnn.zfill(4) +".jpg", dpi=300)
        
        plt.close()
        
        n += 1
    
    optime+=dt
    time+=dt


