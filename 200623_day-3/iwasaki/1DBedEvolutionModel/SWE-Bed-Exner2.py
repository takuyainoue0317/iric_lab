# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 16:13:50 2019

@author: river801
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

def alf(bet):
    if bet>20:
        alfx = bet
    else:
        alfx = bet/(1.-np.exp(-bet))
    
    return alfx

def ent_gp(zet):
    
    aa = 1.3*10**(-7)
    
    ent = aa*zet**5./(1.+aa*zet**5./0.3)
    
    return ent
    

# set workiing directly and file name

tuk   = 100.
etime = tuk*3600.

# Setting the river geometry and model parameters

g = 9.81
nu = 0.000001

dis    = 200.
chlen  = 2000       # length of river reach (m)
wid    = 200            # channel width (m)
snm    = 0.03           # mannings roughness coefs
ib     = 0.002      # bed slope
spec   = 1.65
diam   = 0.0002
tsc    = 0.05
poro   = 0.4
hdown  = 3.


rep = (spec*g*diam**3.)**0.5/nu
b1 = 2.891394
b2 = 0.95296
b3 = 0.056835
b4 = 0.002892
b5 = 0.000245
wf = np.exp(-b1+b2*np.log(rep)-b3*(np.log(rep))**2.-b4*(np.log(rep))**3.+b5*(np.log(rep))**4.)*(spec*g*diam)**0.5

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
c   = np.zeros(nx+1)
wc  = np.zeros(nx+1)
dd  = np.zeros(nx+1)
ee  = np.zeros(nx+1)

x[0] = 0.

for i in np.arange(1,nx+1):
    x[i] = x[i-1]+dx
    

z[0] = chlen*ib

for i in np.arange(1,nx+1):
    z[i] = z[i-1]-ib*dx
    
#for i in np.arange(1,nx+1):
#    if 0.45*nx < i < 0.55*nx:
##        z[i] = z[i] + 0.3*h0
        
for i in np.arange(1,nx+1):
    eta[i] = (z[i-1]+z[i])*0.5
    xc[i] = (x[i-1]+x[i])*0.5
    
h0 = (snm*dis/(wid*ib**0.5))**0.6

for i in np.arange(1,nx+1):
    hh = hdown-eta[i]
    if hh>h0:
        h[i] = hh
        u[i] = dis/wid/h[i]
        q[i] = dis/wid
    else:
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
    
    u[0] = dis/(h0*wid)
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
        
#    h[nx] = h[nx-1]
    h[nx] = hdown
    
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
    
    wc = c
    
#    usta = (g*(snm*u[0])**2./(h[0]**(1./3.)))**0.5
#    beta = 15.*wf/usta
#    zet  = usta/wf*rep**0.6
#    wc[0] = ent_gp(zet)/alf(beta)
    
    usta = (g*(snm*u[0])**2./(h[0]**(1./3.)))**0.5
    beta = 15.*wf/usta
    zet  = usta/wf*rep**0.6
    wc[0] = ent_gp(zet)/alf(beta)
    
    for i in np.arange(1,nx+1):
        uc = (u[i]+u[i-1])*0.5
        usta = (g*(snm*uc)**2./(h[i]**(1./3.)))**0.5
        beta = 15.*wf/usta
        zet  = usta/wf*rep**0.6
        
        dd[i] = wc[i]*alf(beta)*wf
        ee[i] = ent_gp(zet)*wf
        
        c[i] = wc[i]+(-(q[i]*wc[i]-q[i-1]*wc[i-1])/dx+ee[i]-dd[i])*dt/h[i]
        
    
    
    if time>1000:
    
        for i in np.arange(1,nx+1):
            eta[i] = eta[i]-(-qb[i-1]+qb[i])/dx*dt/(1.-poro) + (dd[i]-ee[i])*dt/(1.-poro)
    
    if optime>tuk:
        print("Time= ",time/3600)
        optime = optime-tuk
        
        hh = h+eta
        
        plt.xlim([0,chlen])
        plt.ylim([0,chlen*ib+h0*1.3])
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


