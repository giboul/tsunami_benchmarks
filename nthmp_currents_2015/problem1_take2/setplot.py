
""" 
Set up the plot figures, axes, and items to be done for each frame.

This module is imported by the plotting routines and then the
function setplot is called to set the plot parameters.
    
""" 
from pylab import nonzero, where, ravel, sqrt, plot, quiver,contour
from clawpack.visclaw import colormaps, geoplot, gaugetools
# raise ImportError("Uncomment this to get error and get prompted to use `clawpack.visclaw.setplot_default()`")


def find(condition):
    return nonzero(ravel(condition))


#--------------------------
def setplot(plotdata):
#--------------------------
    
    """ 
    Specify what is to be plotted at each frame.
    Input:  plotdata, an instance of pyclaw.plotters.data.ClawPlotData.
    Output: a modified version of plotdata.
    
    """ 

    plotdata.clearfigures()  # clear any old figures,axes,items data
    plotdata.format = 'binary'

    def set_drytol(current_data):
        # The drytol parameter is used in masking land and water and
        # affects what color map is used for cells with small water depth h.
        # The cell will be plotted as dry if h < drytol.
        # The best value to use often depends on the application and can
        # be set here (measured in meters):
        current_data.user['drytol'] = 1.e-2

    plotdata.beforeframe = set_drytol

    # To plot gauge locations on imshow or contour plot, use this as
    # an afteraxis function:

    def addgauges(current_data):
        gaugetools.plot_gauge_locations(current_data.plotdata, \
             gaugenos='all', format_string='ko', add_labels=True, fontsize=8)
    
    #-----------------------------------------
    # Figure for imshow plot
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='surface', figno=0)
    plotfigure.kwargs = {'figsize':(14,10)}

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('surface')
    plotaxes.axescmd = 'subplot(311)'
    #plotaxes.axescmd = 'axes([.1,.7,.8,.2])'
    plotaxes.title = 'Surface'
    plotaxes.scaled = True
    plotaxes.xlimits = [0,9.5]

    cmap = colormaps.make_colormap({0:[0.5,1,0.5],0.01:[0,1,1], \
                                    0.2:[0,0,1], 0.5:[1,1,0],  0.8:[1,0,0], \
                                    1.:[0.2,0,0]})

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    #plotitem.plot_var = geoplot.surface
    plotitem.plot_var = geoplot.surface_or_depth
    plotitem.imshow_cmap = cmap
    plotitem.imshow_cmin = -0.003
    plotitem.imshow_cmax = 0.003
    plotitem.add_colorbar = True
    plotitem.colorbar_shrink = 0.6
    plotitem.amr_celledges_show = [0]
    plotitem.amr_patchedges_show = [0]

    # Add contour lines of bathymetry:
    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    plotitem.plot_var = geoplot.topo
    plotitem.contour_levels = [-0.05, -0.01]
    plotitem.amr_contour_colors = ['k']  # color on each level
    plotitem.kwargs = {'linestyles':'solid'}
    plotitem.amr_contour_show = [0,1]
    plotitem.celledges_show = 0
    plotitem.patchedges_show = 0
    plotitem.show = True

    #-----------------------------------------
    # Figure for cross section
    #-----------------------------------------
    #plotfigure = plotdata.new_plotfigure(name='cross-section', figno=1)
    #plotfigure.show = False
    #plotfigure.kwargs = {'figsize':(14,7)}

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.axescmd = 'subplot(312)'
    plotaxes.xlimits = [0,12]
    plotaxes.ylimits = [-0.03,0.01]
    plotaxes.title = 'Cross section of surface at y=0.76'

    plotitem = plotaxes.new_plotitem(plot_type='1d_from_2d_data')

    def xsec(current_data):
        # Return x value and surface eta at this point, along y=0.76
        x = current_data.x
        y = current_data.y
        dy = current_data.dy
        q = current_data.q

        ij = find((y <= 0.76+dy/2.) & (y > 0.76-dy/2.))
        x_slice = ravel(x)[ij]
        eta_slice = ravel(q[3,:,:])[ij]
        return x_slice, eta_slice


    plotitem.map_2d_to_1d = xsec
    plotitem.plotstyle = 'kx'     ## need to be able to set amr_plotstyle
    plotitem.kwargs = {'markersize':3}
    plotitem.amr_show = [1]  # plot on all levels

    plotitem = plotaxes.new_plotitem(plot_type='1d_from_2d_data')
    #plotitem.show = False

    def xsec_B(current_data):
        # Return x value and B at this point, along y=0
        x = current_data.x
        y = current_data.y
        dy = current_data.dy
        q = current_data.q
        h = q[0,:]
        eta = q[3,:]
        B = eta - h

        ij = find((y <= 0.76+dy/2.) & (y > 0.76-dy/2.))
        x_slice = ravel(x)[ij]
        B_slice = ravel(B)[ij]
        return x_slice, B_slice

    plotitem.map_2d_to_1d = xsec_B
    plotitem.plotstyle = 'g+'     ## need to be able to set amr_plotstyle
    plotitem.kwargs = {'markersize':3}
    plotitem.amr_show = [1]  # plot on all levels


    plotaxes = plotfigure.new_plotaxes()
    plotaxes.axescmd = 'subplot(313)'
    plotaxes.xlimits = [0,12]
    plotaxes.ylimits = [-0.2,0.3]
    plotaxes.title = 'u-velocity'
    plotitem = plotaxes.new_plotitem(plot_type='1d_from_2d_data')

    def xsec_s(current_data):
        # Return x value and speed at this point, along y=0
        x = current_data.x
        y = current_data.y
        dy = current_data.dy
        q = current_data.q
        h = q[0,:]
        dry_tol = 0.001
        u = where(h>dry_tol, q[1,:]/h, 0.)
        v = where(h>dry_tol, q[2,:]/h, 0.)
        #s = sqrt(u**2 + v**2)
        #s = s / sqrt(9.81/0.97)  # so comparable to eta

        ij = find((y <= 0.76+dy/2.) & (y > 0.76-dy/2.))
        x_slice = ravel(x)[ij]
        #s_slice = ravel(s)[ij]
        u_slice = ravel(u)[ij]
        return x_slice, u_slice

    plotitem.map_2d_to_1d = xsec_s
    plotitem.plotstyle = 'bo'     ## need to be able to set amr_plotstyle
    plotitem.kwargs = {'markersize':3}
    plotitem.amr_show = [1]  # plot on all levels


    plotaxes = plotfigure.new_plotaxes()
    plotaxes.show = False
    plotaxes.axescmd = 'subplot(414)'
    plotaxes.xlimits = [0,12]
    plotaxes.ylimits = [0.004,0.008]
    plotaxes.title = 'discharge'
    plotitem = plotaxes.new_plotitem(plot_type='1d_from_2d_data')

    def xsec_hu(current_data):
        # Return x value and discharge at this point, along y=0
        x = current_data.x
        y = current_data.y
        dy = current_data.dy
        q = current_data.q
        hu = q[1,:]
        ij = find((y <= 0.76+dy/2.) & (y > 0.76-dy/2.))
        x_slice = ravel(x)[ij]
        hu_slice = ravel(hu)[ij]
        return x_slice, hu_slice

    plotitem.map_2d_to_1d = xsec_hu
    plotitem.plotstyle = 'bo'     ## need to be able to set amr_plotstyle
    plotitem.kwargs = {'markersize':3}
    plotitem.amr_show = [1]  # plot on all levels






    #-----------------------------------------
    # Figure for quiver plot
    #-----------------------------------------

    plotfigure = plotdata.new_plotfigure(name='quiver', figno=8)
    plotfigure.show = False
    plotfigure.kwargs = {'figsize':(14,8)}

    def speed(current_data):
        q = current_data.q
        h = q[0,:]
        dry_tol = 0.001
        u = where(h>dry_tol, q[1,:]/h, 0.)
        v = where(h>dry_tol, q[2,:]/h, 0.)
        s = sqrt(u**2 + v**2)
        return s

    def plot_quiver(current_data):
        if current_data.level < 2:
            return
        q = current_data.q
        x = current_data.x
        y = current_data.y
        h = q[0,:,:]
        dry_tol = 0.001
        u = where(h>dry_tol, q[1,:,:]/h, 0.) #  - 0.115 # for relative vel.
        v = where(h>dry_tol, q[2,:,:]/h, 0.)
        c = 8  # coarsening factor
        quiver(x[::c,::c],y[::c,::c],u[::c,::c],v[::c,::c],scale=10)
        B = q[3,:,:] - h
        contour(x,y,B,[-0.05,-0.01],colors='b',linestyles='solid',linewidths=2)
        #print "+++ B: ",B.min(), B.max()
        if h.min() < 0.003:
            print(f"+++ h.min: {h.min()}")



    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = 'Velocity'
    plotaxes.scaled = True
    plotaxes.xlimits = [4.5,7.5]

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = speed
    #plotitem.imshow_cmap = colormaps.white_red
    #plotitem.imshow_cmap = colormaps.yellow_red_blue
    plotitem.imshow_cmap = \
           colormaps.make_colormap({0:[1,1,1],0.5:[0.5,0.5,1],1:[1,0.3,0.3]})
    plotitem.imshow_cmin = 0.
    plotitem.imshow_cmax = 0.23
    plotitem.add_colorbar = True
    plotitem.amr_celledges_show = [0]
    plotitem.amr_patchedges_show = [0]
    plotitem.afterpatch = plot_quiver




    #-----------------------------------------
    # Figure for vorticity plot
    #-----------------------------------------

    plotfigure = plotdata.new_plotfigure(name='vorticity', figno=9)
    #plotfigure.show = False
    #plotfigure.kwargs = {'figsize':(16,6)}
    plotfigure.kwargs = {'figsize':(16,12)}


    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.axescmd = 'subplot(211)'
    plotaxes.title = 'Vorticity'
    plotaxes.scaled = True
    plotaxes.xlimits = [4.5,9.5]

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = 4
    plotitem.imshow_cmap = colormaps.blue_white_red
    plotitem.imshow_cmin = -0.5
    plotitem.imshow_cmax = 0.5
    plotitem.add_colorbar = True
    plotitem.colorbar_shrink = 0.6
    plotitem.amr_celledges_show = [0]
    plotitem.amr_patchedges_show = [0]
    #plotitem.afterpatch = plot_quiver

    # Add contour lines of bathymetry:
    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    plotitem.plot_var = geoplot.topo
    plotitem.contour_levels = [-0.05, -0.01]
    plotitem.amr_contour_colors = ['k']  # color on each level
    plotitem.kwargs = {'linestyles':'solid'}
    plotitem.amr_contour_show = [0,1]
    plotitem.celledges_show = 0
    plotitem.patchedges_show = 0
    plotitem.show = True

    # Set up for axes for velocity
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.axescmd = 'subplot(212)'
    plotaxes.title = 'Velocity'
    plotaxes.scaled = True
    plotaxes.xlimits = [4.5,9.5]

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = speed
    #plotitem.imshow_cmap = colormaps.white_red
    #plotitem.imshow_cmap = colormaps.yellow_red_blue
    plotitem.imshow_cmap = \
           colormaps.make_colormap({0:[1,1,1],0.5:[0.5,0.5,1],1:[1,0.3,0.3]})
    plotitem.imshow_cmin = 0.
    plotitem.imshow_cmax = 0.115 * 2
    plotitem.add_colorbar = True
    plotitem.colorbar_shrink = 0.6
    plotitem.amr_celledges_show = [0]
    plotitem.amr_patchedges_show = [0]
    plotitem.afterpatch = plot_quiver



    #-----------------------------------------
    # Figure for zoom plot
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='zoom', figno=2)
    plotfigure.show = False
    plotfigure.kwargs = {'figsize':(14,10)}

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes('surface')
    plotaxes.title = 'Surface'
    plotaxes.scaled = True
    plotaxes.afteraxes = addgauges

    # Water
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    #plotitem.plot_var = geoplot.surface
    plotitem.plot_var = geoplot.surface_or_depth
    plotitem.imshow_cmap = cmap
    plotitem.imshow_cmin = 0.
    plotitem.imshow_cmax = 0.2
    plotitem.add_colorbar = True
    plotitem.amr_celledges_show = [0]
    plotitem.amr_patchedges_show = [0]

    # Land
    plotitem = plotaxes.new_plotitem(plot_type='2d_imshow')
    plotitem.plot_var = geoplot.land
    plotitem.imshow_cmap = geoplot.land_colors
    plotitem.imshow_cmin = 0.0
    plotitem.imshow_cmax = 0.3
    plotitem.add_colorbar = False
    plotitem.amr_celledges_show = [0]
    plotaxes.xlimits = [32,42]
    plotaxes.ylimits = [-6,3]

    # Add contour lines of bathymetry:
    plotitem = plotaxes.new_plotitem(plot_type='2d_contour')
    plotitem.plot_var = geoplot.topo
    plotitem.contour_levels = [0.08]
    plotitem.amr_contour_colors = ['k']  # color on each level
    plotitem.kwargs = {'linestyles':'solid'}
    plotitem.amr_contour_show = [0,1]
    plotitem.celledges_show = 0
    plotitem.patchedges_show = 0
    plotitem.show = True



    #-----------------------------------------
    # Figures for gauges
    #-----------------------------------------

    def add_zeroline(current_data):
        t = current_data.t
        plot(t, 0*t, 'k')

    plotfigure = plotdata.new_plotfigure(name='Surface & topo', figno=300, \
                    type='each_gauge')

    plotfigure.kwargs = {'figsize':(14,9)}
    plotfigure.clf_each_gauge = True

    # Set up for axes in this figure:

    plotaxes = plotfigure.new_plotaxes()
    plotaxes.axescmd = 'subplot(3,1,1)'
    #plotaxes.ylimits = [-0.1, 0.2]
    plotaxes.title = 'Surface'
    plotaxes.afteraxes = add_zeroline

    # Plot surface as blue curve:
    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = 3
    plotitem.plotstyle = 'b-'

    # u-velocity
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.axescmd = 'subplot(3,1,2)'
    #plotaxes.ylimits = [-0.1, 0.2]
    plotaxes.title = 'u-velocity'

    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    def u(current_data):
        q = current_data.q
        h = q[0,:]
        dry_tol = 0.001
        u = where(h>dry_tol, q[1,:]/h, 0.)
        v = where(h>dry_tol, q[2,:]/h, 0.)
        return u

    plotitem.plot_var = u
    plotitem.plotstyle = 'b-'


    # v-velocity
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.axescmd = 'subplot(3,1,3)'
    #plotaxes.ylimits = [-0.1, 0.2]
    plotaxes.title = 'v-velocity'

    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    def v(current_data):
        q = current_data.q
        h = q[0,:]
        dry_tol = 0.001
        u = where(h>dry_tol, q[1,:]/h, 0.)
        v = where(h>dry_tol, q[2,:]/h, 0.)
        return v

    plotitem.plot_var = v
    plotitem.plotstyle = 'b-'


    plotaxes.afteraxes = add_zeroline


    #-----------------------------------------
    # Figure for patches alone
    #-----------------------------------------
    plotfigure = plotdata.new_plotfigure(name='patches', figno=22)
    plotfigure.show = False

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = [0,1]
    plotaxes.ylimits = [0,1]
    plotaxes.title = 'patches'
    plotaxes.scaled = True

    # Set up for item on these axes:
    plotitem = plotaxes.new_plotitem(plot_type='2d_patch')
    plotitem.amr_patch_bgcolor = ['#ffeeee', '#eeeeff', '#eeffee']
    plotitem.amr_celledges_show = [1,1,0]   
    plotitem.amr_patchedges_show = [1]     

    #-----------------------------------------
    
    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via pyclaw.plotters.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = 'all'          # list of frames to print
    plotdata.print_gaugenos = 'all'          # list of gauges to print
    plotdata.print_fignos = 'all'            # list of figures to print
    plotdata.html = True                     # create html files of plots?
    plotdata.html_homelink = '../README.html'   # pointer for top of index
    plotdata.latex = True                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?

    return plotdata

    
