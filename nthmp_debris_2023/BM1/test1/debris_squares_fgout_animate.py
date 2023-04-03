"""
Plot fgout frames and also motion of particles using velocities
interpolated from fgout.
"""

import sys
if 'matplotlib' not in sys.modules:
    import matplotlib
    #matplotlib.use('Agg')  # Use an image backend


from pylab import *
import os,sys
from matplotlib import colors
import matplotlib.animation as animation
from clawpack.visclaw import animation_tools, plottools, geoplot


#import postproc_fgout as P
#CMH = os.environ['CMH'] 
#sys.path.append(os.path.join(CMH,'common_python'))   
#import fgout_tools2
import fgout_particles as P


if 1:
    from clawpack.geoclaw import fgout_tools
    graphics_dir = os.path.abspath('../../../graphics')
else:
    # local versions for self-contained directory:
    import fgout_tools
    graphics_dir = './'
    
outdir = os.path.abspath('_output')

if 'mmfs1' in outdir:
    # on hyak:
    outdir = outdir.replace('mmfs1/home','gscratch/tsunami')

print('Looking for output in ',outdir)

output_format = 'binary32'

# List of frames to use for making debris paths and animation:
fgframes = range(10,40)
#fgframes = [1,20,40]


bgimage = None
plot_extent = [34, 43.75, -3, 3]
color = 'k'
linewidth = 2

# stationary block:
x1b = 35.54
x2b = 36.14
y1b = 1.22
y2b = y1b + 0.6

outdir = '_output'
format = 'binary32'  # format of fgout grid output

# Instantiate object for reading fgout frames:
fgout_grid = fgout_tools.FGoutGrid(1, outdir, output_format)


# Deterime time t0 of first fgout frame, to initialize particles
frameno0 = fgframes[0]
fgout0 = fgout_grid.read_frame(frameno0)
t0 = fgout0.t


def timeformat(t):
    """
    Convert t in seconds to string in format hh:mm:ss
    """
    from numpy import mod
    hours = int(t/3600.)
    tmin = mod(t,3600.)
    min = int(tmin/60.)
    sec = int(mod(tmin,60.))
    timestr = '%s:%s:%s' % (hours,str(min).zfill(2),str(sec).zfill(2))
    return timestr

def timeformat(t): 
    timestr = '%.3f seconds' % t   
    return timestr
    
# Initialize debris_paths dictionary and set
# initial debris particle locations (x0,y0) at time t0.
# Require a list of dbnos and each array 
#     debris_paths[dbno]
# in the dictionary is a 2d array with a single row [t0, x0, y0] to start.

debris_paths = {}
grounding_depth = {}
drag_factor = {}
mass = {}
dradius = {}
Kspring = 50.
nsubsteps = 20


dbnos = []
dbnosA = []
dbnosB = []
# set initial velocities to 0 (or may want to interpolate from fgout0 if t0>0?)
u0 = 0.
v0 = 0.
length = 0.6 # * sqrt(2)

xg1 = [34.34] #, 34.94]
yg1 = [0.82] #, 0.82]
xgg = [35.54]
ygg = [1.22]
for xg in xg1:
    for yg in yg1:
        xgg.append(xg)
        ygg.append(yg)
    
grounding_depth_common = 0. #0.04
drag_factor_common = 1.
mass_common = 1.
dradius_common = 0.2

#Ktether = {}
#Ktether_common = 50.

def tether(dbno1,dbno2):
    if abs(dbno1-dbno2) in [1000,3000]:
        # adjecent sides of square
        Dtether = length
        Ktether = 50.
    elif abs(dbno1-dbno2) == 2000:
        # diagonal of square
        Dtether = length * sqrt(2)
        Ktether = 50.
    else:
        Dtether = nan
        Ktether = 0.
    return Dtether,Ktether

for k in range(len(xgg)):
    dbno = k
    db = array([[t0, xgg[k], ygg[k], u0, v0]])
    debris_paths[dbno] = db
    dbnos.append(dbno)
    dbnosA.append(dbno)  # debris at lower left corner
    grounding_depth[dbno] = grounding_depth_common
    drag_factor[dbno] = drag_factor_common
    mass[dbno] = mass_common
    dradius[dbno] = dradius_common
    
    # add paired particles for square debris:
    dbno1 = dbno + 1000
    #Ktether[(dbno,dbno1)] = Ktether_common
    #Ktether[(dbno1,dbno)] = Ktether_common
    db = array([[t0, xgg[k], ygg[k]+length, u0, v0]])
    debris_paths[dbno1] = db
    dbnos.append(dbno1)
    grounding_depth[dbno1] = grounding_depth_common
    drag_factor[dbno1] = drag_factor_common 
    mass[dbno1] = mass_common
    dradius[dbno1] = dradius_common

    dbno2 = dbno + 2000
    #Ktether[(dbno1,dbno2)] = Ktether_common
    #Ktether[(dbno2,dbno1)] = Ktether_common
    db = array([[t0, xgg[k]+length, ygg[k]+length, u0, v0]])
    debris_paths[dbno2] = db
    dbnos.append(dbno2)
    grounding_depth[dbno2] = grounding_depth_common
    drag_factor[dbno2] = drag_factor_common 
    mass[dbno2] = mass_common
    dradius[dbno2] = dradius_common
    
    dbno3 = dbno + 3000
    #Ktether[(dbno2,dbno3)] = Ktether_common
    #Ktether[(dbno3,dbno2)] = Ktether_common
    #Ktether[(dbno,dbno3)] = Ktether_common
    #Ktether[(dbno3,dbno)] = Ktether_common
    #Ktether[(dbno,dbno2)] = Ktether_common
    #Ktether[(dbno2,dbno)] = Ktether_common
    #Ktether[(dbno1,dbno3)] = Ktether_common
    #Ktether[(dbno3,dbno1)] = Ktether_common
    db = array([[t0, xgg[k]+length, ygg[k], u0, v0]])
    debris_paths[dbno3] = db
    dbnos.append(dbno3)
    grounding_depth[dbno3] = grounding_depth_common
    drag_factor[dbno3] = drag_factor_common 
    mass[dbno3] = mass_common
    dradius[dbno3] = dradius_common
    
for dbno in dbnos:
    if mod(dbno,1000) == 0:
        mass[dbno] = 1e6

print('Created %i initial debris particles' % len(dbnos))
#import pdb; pdb.set_trace()

                     
# Compute debris path for each particle by using all the fgout frames
# in the list fgframes (first frame should be frameno0 used to set t0 above):

debris_paths = P.make_debris_paths_substeps(fgout_grid, fgframes, debris_paths,
                      dbnos, drag_factor, grounding_depth, 
                      mass, dradius, Kspring, tether, nsubsteps)

def make_dbABCD(t, debris_paths, dbnosA):
    xdAB = []
    ydAB = []
    
    for k in range(len(dbnosA)):
        dbnoA = dbnosA[k]
        dbnoB = dbnoA + 1000
        dbnoC = dbnoA + 2000
        dbnoD = dbnoA + 3000
        dbA = debris_paths[dbnoA]
        dbB = debris_paths[dbnoB]
        dbC = debris_paths[dbnoC]
        dbD = debris_paths[dbnoD]
        try:
            j = where(abs(dbA[:,0]-t) < 1e-6)[0].max()
        except:
            print('Did not find path for dbno=%i at t = %.3f' % (dbno,t))
            j = -1
        if j > -1:
            xA = dbA[j,1]
            yA = dbA[j,2]
            xB = dbB[j,1]
            yB = dbB[j,2]
            xC = dbC[j,1]
            yC = dbC[j,2]
            xD = dbD[j,1]
            yD = dbD[j,2]
            xdAB = xdAB + [xA,xB,xC,xD,xA,nan]
            ydAB = ydAB + [yA,yB,yC,yD,yA,nan]
            #import pdb; pdb.set_trace()
    xdAB = array(xdAB)
    ydAB = array(ydAB)
    #print('+++ xdAB = ',xdAB)
    #print('+++ ydAB = ',ydAB)
    return xdAB,ydAB



# First initialize plot with data from initial frame,
# do this in a way that returns an object for each plot attribute that
# will need to be changed in subsequent frames.
# In tis case, the color image of the water depth, plots of particles, and 
# title (which includes the time) will change.
# The background image, colorbar, etc. do not change.

fgout = fgout0
ylat = fgout.Y.mean()  # for aspect ratio of plots

fig,ax = subplots(figsize=(8,7))

ax.set_xlim(plot_extent[:2])
ax.set_ylim(plot_extent[2:])

ax.plot([x1b,x2b,x2b,x1b,x1b], [y1b,y1b,y2b,y2b,y1b], 'g')

if 1:
    # speed
    s_units = 'm/s'
    if s_units == 'knots':
        s = fgout.s * 1.9438  # convert m/s to knots
        bounds_speed = np.array([1e-3,3,4,6,9,12])  # knots
    else:
        s = fgout.s
        bounds_speed = np.array([1e-3,1.5,2,3,4.5,6])  # m/s
        bounds_speed = np.array([1e-3,0.1,0.2,0.3,0.4,0.5])  # m/s
        bounds_speed = np.array([1e-3,0.2,0.4,0.6,1.,1.5])  # m/s

    a = 1.
    cmap_speed = mpl.colors.ListedColormap([
                    [.3,.3,1,a],[0,0,1,a], [1,.8,.8,a],[1,.6,.6,a],
                    [1,0,0,a]])

    # Set color for value exceeding top of range to purple:
    cmap_speed.set_over(color=[1,0,1,a])

    if bgimage:
        # Set color to transparent where s < 1e-3:
        cmap_speed.set_under(color=[1,1,1,0])
    else:
        # Set color to white where s < 1e-3:
        cmap_speed.set_under(color=[1,1,1,a])

    norm_speed = colors.BoundaryNorm(bounds_speed, cmap_speed.N)

    im = imshow(flipud(s.T), extent=fgout.extent_edges,
                cmap=cmap_speed, norm=norm_speed)
    cb = colorbar(im, extend='max', shrink=0.7)
    cb.set_label(s_units)
    #contour(fgout.X, fgout.Y, fgout.B, [0], colors='g', linewidths=0.5)

    #ax.set_aspect(1./cos(ylat*pi/180.))
    ticklabel_format(useOffset=False)
    xticks(rotation=20)
    ax.set_xlim(plot_extent[:2])
    ax.set_ylim(plot_extent[2:])

    t = fgout.t
    t_str = timeformat(t)
    title_text = title('Speed at t = %s' % t_str)

if 0:
    # depth

    a = 1.
    cmap_depth = mpl.colors.ListedColormap([
                    [.3,.3,1,a],[0,0,1,a], [1,.8,.8,a],[1,.6,.6,a],
                    [1,0,0,a]])

    # Set color for value exceeding top of range to purple:
    cmap_depth.set_over(color=[1,0,1,a])

    if bgimage:
        # Set color to transparent where s < 1e-3:
        cmap_depth.set_under(color=[1,1,1,0])
    else:
        # Set color to white where s < 1e-3:
        cmap_depth.set_under(color=[1,1,1,a])

    bounds_depth = np.array([0,1,2,3,4,5])
    norm_depth = colors.BoundaryNorm(bounds_depth, cmap_depth.N)
    
    #eta_water = where(fgout.h>0, fgout.h, nan)
    eta_water = np.ma.masked_where(fgout.h < 1e-3, fgout.eta)
    
    im = imshow(flipud(eta_water.T), extent=fgout.extent_edges,
                    cmap=geoplot.tsunami_colormap)
                    #cmap=cmap_depth, norm=norm_depth)
    im.set_clim(-5,5)
                
    cb = colorbar(im, extend='max', shrink=0.7)
    cb.set_label('meters')
    #contour(fgout.X, fgout.Y, fgout.B, [0], colors='g', linewidths=0.5)

    ax.set_aspect(1./cos(ylat*pi/180.))
    ticklabel_format(useOffset=False)
    xticks(rotation=20)
    ax.set_xlim(plot_extent[:2])
    ax.set_ylim(plot_extent[2:])

    t = fgout.t
    t_str = timeformat(t)
    title_text = title('Surface/depth at t = %s' % t_str)

xdAB,ydAB = make_dbABCD(t, debris_paths, dbnosA)
pairs, = ax.plot(xdAB, ydAB, color=color, linestyle='-', linewidth=linewidth)


print('+++ pairs = ',pairs)

# The function update below should have arguments num (for the frame number)
# plus things listed here in fargs.

fargs = (im,pairs,title_text)

# fargs should be initialized above and are the plot Artist objects 
# whose data change from one frame to the next.


def update(num, im, pairs, title_text):
    
    fgframe = fgframes[num]
    # note: uses fgframes to specify fgout frames to use
    
    # Read fgout data for this frame:
    #fgout = P.read_fgout_frame(fgno, fgframe, plotdata)
    fgout = fgout_grid.read_frame(fgframe)
    
    # Reset the plot objects that need to change from previous frame:

    # title:
    t = fgout.t        
    t_str = timeformat(t)
    title_text.set_text('Speed at t = %s' % t_str)
    
    # color image:
    eta_water = np.ma.masked_where(fgout.h < 1e-3, fgout.eta)
    #im.set_data(flipud(eta_water.T))
    im.set_data(flipud(fgout.s.T))

    # particle locations:
    
    xdAB,ydAB = make_dbABCD(t, debris_paths, dbnosA)
    pairs.set_data(xdAB, ydAB)
        
    # must now return all the objects listed in fargs:
    return im,pairs,title_text

print('Making anim...')
anim = animation.FuncAnimation(fig, update,
                               frames=len(fgframes), 
                               fargs=fargs,
                               interval=200, blit=True)

fname_mp4 = 'debris_pairs.mp4'
fps = 5
print('Making mp4...')
animation_tools.make_mp4(anim, fname_mp4, fps)
