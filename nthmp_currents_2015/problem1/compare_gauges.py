from pylab import *
from clawpack.visclaw.data import ClawPlotData


plotdata = ClawPlotData()

if True:
    plotdata.outdir = '_output'
    toffset = 0.
elif True:
    plotdata.outdir = '_output_manning_0.025'
    toffset = 92.
elif False:
    plotdata.outdir = '_output_manning015_cfl090'
    toffset = 92.
else:
    plotdata.outdir = '_output_manning015_cfl089'
    toffset = 96.
print(f"USING OUTPUT FOLDER: {plotdata.outdir}")

figure(50,figsize=(18,12))
clf()

# ---  Gauge 1 ---

d = loadtxt('../problem1_take2/S1u.txt')
t1u = d[:,0]
s1u = d[:,1]

d = loadtxt('../problem1_take2/S1v.txt')
t1v = d[:,0]
s1v = d[:,1]

g = plotdata.getgauge(1)
print(g)
u = g.q[1,:] / g.q[0,:]
v = g.q[2,:] / g.q[0,:]


subplot(4,1,1)
plot(t1u+toffset,s1u,'b',label='Experiment')
plot(g.t, u, 'r',label='GeoClaw')
ylabel('u (m/s)')
legend(loc='upper right')

subplot(4,1,2)
plot(t1v+toffset,s1v,'b',label='Experiment')
plot(g.t, v, 'r',label='GeoClaw')
ylabel('v (m/s)')

# ---  Gauge 2 ---

d = loadtxt('../problem1_take2/S2u.txt')
t2u = d[:,0]
s2u = d[:,1]

d = loadtxt('../problem1_take2/S2v.txt')
t2v = d[:,0]
s2v = d[:,1]

g = plotdata.getgauge(2)
u = g.q[1,:] / g.q[0,:]
v = g.q[2,:] / g.q[0,:]

subplot(4,1,3)
plot(t2u+toffset,s2u,'b',label='Experiment')
plot(g.t, u, 'r',label='GeoClaw')
ylabel('u (m/s)')
legend(loc='upper right')

subplot(4,1,4)
plot(t2v+toffset,s2v,'b',label='Experiment')
plot(g.t, v, 'r',label='GeoClaw')
ylabel('v (m/s)')

show()
#savefig('gauges_manning015_cfl089.png')
