"""
Module to set up run time parameters for Clawpack.

The values set in the function setrun are then written out to data files
that will be read in by the Fortran code.

"""

import numpy as np
from clawpack.clawutil.data import ClawRunData


#------------------------------
def setrun(claw_pkg='geoclaw'):
#------------------------------

    """
    Define the parameters used for running Clawpack.

    Return
    ------
        rundata - object of class ClawRunData

    """

    num_dim = 2
    rundata = ClawRunData('geoclaw', num_dim)

    #------------------------------------------------------------------
    # GeoClaw specific parameters:
    #------------------------------------------------------------------
    rundata = setgeo(rundata)

    #------------------------------------------------------------------
    # Standard Clawpack parameters to be written to claw.data:
    #   (or to amr2ez.data for AMR)
    #------------------------------------------------------------------
    clawdata = rundata.clawdata  # initialized when rundata instantiated


    # Set single grid parameters first.
    # See below for AMR parameters.


    # ---------------
    # Spatial domain:
    # ---------------

    # Number of space dimensions:
    clawdata.num_dim = num_dim

    # Lower and upper edge of computational domain:
    clawdata.lower[0] = 0.0
    clawdata.upper[0] = 43.75

    clawdata.lower[1] = -13.3
    clawdata.upper[1] = 13.3



    # Number of grid cells: Coarsest grid
    clawdata.num_cells[0] = 88
    clawdata.num_cells[1] = 54
    #clawdata.num_cells[0] = 200
    #clawdata.num_cells[1] = 10


    # ---------------
    # Size of system:
    # ---------------

    # Number of equations in the system:
    clawdata.num_eqn = 3

    # Number of auxiliary variables in the aux array (initialized in setaux)
    clawdata.num_aux = 1

    # Index of aux array corresponding to capacity function, if there is one:
    clawdata.capa_index = 0

    
    
    # -------------
    # Initial time:
    # -------------

    clawdata.t0 = 0.0


    # Restart from checkpoint file of a previous run?
    # Note: If restarting, you must also change the Makefile to set:
    #    RESTART = True
    # If restarting, t0 above should be from original run, and the
    # restart_file 'fort.chkNNNNN' specified below should be in 
    # the OUTDIR indicated in Makefile.

    clawdata.restart = False               # True to restart from prior results
    clawdata.restart_file = 'fort.chk00006'  # File to use for restart data

    # -------------
    # Output times:
    #--------------

    # Specify at what times the results should be written to fort.q files.
    # Note that the time integration stops after the final output time.
    # The solution at initial time t0 is always written in addition.

    clawdata.output_style = 1

    if clawdata.output_style==1:
        # Output nout frames at equally spaced times up to tfinal:
        clawdata.num_output_times = 5
        clawdata.tfinal = 35.0
        clawdata.output_t0 = False  # output at initial (or restart) time?

    elif clawdata.output_style == 2:
        # Specify a list of output times.
        clawdata.output_times = np.linspace(24,40,81)

    elif clawdata.output_style == 3:
        # Output every iout timesteps with a total of ntot time steps:
        clawdata.output_step_interval = 1
        clawdata.total_steps = 1
        clawdata.output_t0 = True
        

    clawdata.output_format = 'binary'      # 'ascii' or 'binary' 

    clawdata.output_q_components = 'all'   # could be list such as [True,True]
    clawdata.output_aux_components = 'none'  # could be list
    clawdata.output_aux_onlyonce = True    # output aux arrays only at t0



    # ---------------------------------------------------
    # Verbosity of messages to screen during integration:
    # ---------------------------------------------------

    # The current t, dt, and cfl will be printed every time step
    # at AMR levels <= verbosity.  Set verbosity = 0 for no printing.
    #   (E.g. verbosity == 2 means print only on levels 1 and 2.)
    clawdata.verbosity = 0



    # --------------
    # Time stepping:
    # --------------

    # if dt_variable==1: variable time steps used based on cfl_desired,
    # if dt_variable==0: fixed time steps dt = dt_initial will always be used.
    clawdata.dt_variable = True

    # Initial time step for variable dt.
    # If dt_variable==0 then dt=dt_initial for all steps:
    clawdata.dt_initial = 0.016

    # Max time step to be allowed if variable dt used:
    clawdata.dt_max = 1e+99

    # Desired Courant number if variable dt used, and max to allow without
    # retaking step with a smaller dt:
    clawdata.cfl_desired = 0.9
    clawdata.cfl_max = 1.0

    # Maximum number of time steps to allow between output times:
    clawdata.steps_max = 5000




    # ------------------
    # Method to be used:
    # ------------------

    # Order of accuracy:  1 => Godunov,  2 => Lax-Wendroff plus limiters
    clawdata.order = 2
    
    # Use dimensional splitting? (not yet available for AMR)
    clawdata.dimensional_split = 'unsplit'
    
    # For unsplit method, transverse_waves can be 
    #  0 or 'none'      ==> donor cell (only normal solver used)
    #  1 or 'increment' ==> corner transport of waves
    #  2 or 'all'       ==> corner transport of 2nd order corrections too
    clawdata.transverse_waves = 2

    # Number of waves in the Riemann solution:
    clawdata.num_waves = 3
    
    # List of limiters to use for each wave family:  
    # Required:  len(limiter) == num_waves
    # Some options:
    #   0 or 'none'     ==> no limiter (Lax-Wendroff)
    #   1 or 'minmod'   ==> minmod
    #   2 or 'superbee' ==> superbee
    #   3 or 'mc'       ==> MC limiter
    #   4 or 'vanleer'  ==> van Leer
    clawdata.limiter = ['mc', 'mc', 'mc']

    clawdata.use_fwaves = True    # True ==> use f-wave version of algorithms
    
    # Source terms splitting:
    #   src_split == 0 or 'none'    ==> no source term (src routine never called)
    #   src_split == 1 or 'godunov' ==> Godunov (1st order) splitting used, 
    #   src_split == 2 or 'strang'  ==> Strang (2nd order) splitting used,  not recommended.
    clawdata.source_split = 'godunov'


    # --------------------
    # Boundary conditions:
    # --------------------

    # Number of ghost cells (usually 2)
    clawdata.num_ghost = 2

    # Choice of BCs at xlower and xupper:
    #   0 => user specified (must modify bcN.f to use this option)
    #   1 => extrapolation (non-reflecting outflow)
    #   2 => periodic (must specify this at both boundaries)
    #   3 => solid wall for systems where q(2) is normal velocity

    clawdata.bc_lower[0] = 'user'
    clawdata.bc_upper[0] = 'wall'

    clawdata.bc_lower[1] = 'wall'
    clawdata.bc_upper[1] = 'wall'

    # Specify when checkpoint files should be created that can be
    # used to restart a computation.

    clawdata.checkpt_style = 0

    if clawdata.checkpt_style == 0:
        # Do not checkpoint at all
        pass

    elif clawdata.checkpt_style == 1:
        # Checkpoint only at tfinal.
        pass

    elif clawdata.checkpt_style == 2:
        # Specify a list of checkpoint times.  
        clawdata.checkpt_times = [0.1,0.15]

    elif clawdata.checkpt_style == 3:
        # Checkpoint every checkpt_interval timesteps (on Level 1)
        # and at the final time.
        clawdata.checkpt_interval = 5

    # ---------------
    # AMR parameters:
    # ---------------
    amrdata = rundata.amrdata

    # max number of refinement levels:
    amrdata.amr_levels_max = 4

    # List of refinement ratios at each level (length at least mxnest-1)
    amrdata.refinement_ratios_x = [4,5,2,2]
    amrdata.refinement_ratios_y = [4,5,2,2]
    amrdata.refinement_ratios_t = [4,5,2,2]


    # Specify type of each aux variable in amrdata.auxtype.
    # This must be a list of length maux, each element of which is one of:
    #   'center',  'capacity', 'xleft', or 'yleft'  (see documentation).

    amrdata.aux_type = ['center']


    # Flag using refinement routine flag2refine rather than richardson error
    amrdata.flag_richardson = False    # use Richardson?
    amrdata.flag2refine = True

    # steps to take on each level L between regriddings of level L+1:
    amrdata.regrid_interval = 3

    # width of buffer zone around flagged points:
    # (typically the same as regrid_interval so waves don't escape):
    amrdata.regrid_buffer_width  = 2

    # clustering alg. cutoff for (# flagged pts) / (total # of cells refined)
    # (closer to 1.0 => more small grids may be needed to cover flagged cells)
    amrdata.clustering_cutoff = 0.700000

    # print info about each regridding up to this level:
    amrdata.verbosity_regrid = 0  


    #  ----- For developers ----- 
    # Toggle debugging print statements:
    amrdata.dprint = False      # print domain flags
    amrdata.eprint = False      # print err est flags
    amrdata.edebug = False      # even more err est flags
    amrdata.gprint = False      # grid bisection/clustering
    amrdata.nprint = False      # proper nesting output
    amrdata.pprint = False      # proj. of tagged points
    amrdata.rprint = False      # print regridding summary
    amrdata.sprint = False      # space/memory output
    amrdata.tprint = False      # time step reporting each level
    amrdata.uprint = False      # update/upbnd reporting
    
    # More AMR parameters can be set -- see the defaults in pyclaw/data.py

    # == setregions.data values ==
    regions = rundata.regiondata.regions
    # to specify regions of refinement append lines of the form
    #  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]
    regions.append([1, 1, 0., 1.e10, -100.,100., -100.,100.])
    regions.append([1, 2, 0., 1.e10,   25.,100.,  -20., 20.])
    regions.append([2, 3, 23.5, 1.e10,   30.,100.,  -8., 20.])
    regions.append([2, 4, 23.5, 1.e10,   32.,43.,  -8., 10.])
    regions.append([4, 4, 23.5, 1.e10,   32.,42.,  -6., 3.])
    #regions.append([5, 5, 23.5, 1.e10,   32.5,39.,  -1., 2.])

    # == setgauges.data values ==
    # for gauges append lines of the form  [gaugeno, x, y, t1, t2]
    # rundata.gaugedata.add_gauge()

    gauges = rundata.gaugedata.gauges
    gauges.append([0, 0.01, 0., 0., 1e10])
    gauges.append([1, 2.068, -0.515, 0., 1e10])
    gauges.append([2, 2.068, 4.065, 0., 1e10])
    gauges.append([3, 18.618, 0., 0., 1e10])
    gauges.append([4, 18.618, 2.86, 0., 1e10])
    gauges.append([5, 5., 0., 0., 1e10])

    # Line A
    gauges.append([101, 33.61, -3.19, 25., 1e10])
    gauges.append([102, 34.10, -3.19, 25., 1e10])
    gauges.append([103, 34.53, -3.18, 25., 1e10])
    gauges.append([104, 35.04, -3.18, 25., 1e10])
    gauges.append([105, 35.54, -3.19, 25., 1e10])
    gauges.append([106, 36.35, -3.20, 25., 1e10])
    gauges.append([107, 37.76, -3.20, 25., 1e10])
    gauges.append([108, 39.22, -3.20, 25., 1e10])
    gauges.append([109, 40.67, -3.23, 25., 1e10])
    
    # Line B
    gauges.append([201, 33.72, -0.59, 25., 1e10])
    gauges.append([202, 34.22, -0.53, 25., 1e10])
    gauges.append([203, 34.68, -0.47, 25., 1e10])
    gauges.append([204, 35.18, -0.41, 25., 1e10])
    gauges.append([205, 35.75, -0.32, 25., 1e10])
    gauges.append([206, 36.64, -0.23, 25., 1e10])
    gauges.append([207, 37.77, -0.07, 25., 1e10])
    gauges.append([208, 39.22,  0.14, 25., 1e10])
    gauges.append([209, 40.67,  0.27, 25., 1e10])
    
    # Line C
    gauges.append([301, 33.81,  1.51, 25., 1e10])
    gauges.append([302, 34.55,  1.60, 25., 1e10])
    gauges.append([303, 35.05,  1.69, 25., 1e10])
    gauges.append([304, 35.56,  1.77, 25., 1e10])
    gauges.append([305, 36.05,  1.85, 25., 1e10])
    gauges.append([306, 37.05,  1.99, 25., 1e10])
    gauges.append([307, 38.24,  2.19, 25., 1e10])
    gauges.append([308, 39.21,  2.34, 25., 1e10])
    gauges.append([309, 40.40,  2.58, 25., 1e10])
    
    # Line D
    gauges.append([401, 35.12,  3.71, 25., 1e10])
    gauges.append([402, 36.68,  3.89, 25., 1e10])
    gauges.append([403, 38.09,  4.07, 25., 1e10])
    gauges.append([404, 38.14,  3.59, 25., 1e10])

    # Virtual gauges suggested by Elena Tolkova:
    gauges.append([501, 33.72 - 1.7, -0.59, 20., 1e10])
    gauges.append([502, 33.72 - 1.2, -0.59, 20., 1e10])
    gauges.append([503, 33.72 - 0.7, -0.59, 20., 1e10])
    gauges.append([504, 33.72 - 0.2, -0.59, 20., 1e10])

    return rundata
    # end of function setrun
    # ----------------------


#-------------------
def setgeo(rundata):
#-------------------
    """
    Set GeoClaw specific runtime parameters.
    For documentation see ....
    """

    if hasattr(rundata, 'geo_data'):
        geo_data = rundata.geo_data
    else:
        raise AttributeError("*** Error, this rundata has no geo_data attribute")

       
    # == Physics ==
    geo_data.gravity = 9.81
    geo_data.coordinate_system = 1
    geo_data.earth_radius = 6367.5e3

    # == Forcing Options
    geo_data.coriolis_forcing = False

    # == Algorithm and Initial Conditions ==
    geo_data.sea_level = 0.0
    geo_data.dry_tolerance = 1.e-3
    geo_data.friction_forcing = True
    geo_data.manning_coefficient = 0.025
    geo_data.friction_depth = 20.0

    # Refinement data
    refinement_data = rundata.refinement_data
    refinement_data.wave_tolerance = 1.e-2
    refinement_data.deep_depth = 1e2
    refinement_data.max_level_deep = 3
    refinement_data.variable_dt_refinement_ratios = True

    # == settopo.data values ==
    topo_data = rundata.topo_data
    # for topography, append lines of the form
    #    [topotype, minlevel, maxlevel, t1, t2, fname]
    #topo_data.topofiles.append([2, 1, 1, 0., 1.e10, 'flat.topotype2'])
    #topo_data.topofiles.append([2, 1, 1, 0., 1.e10, 'seaside_model.topotype2'])
    topo_data.topofiles.append([1, 1, 1, 0., 1.e10, 'pwlinear2.topotype1'])
    topo_data.topofiles.append([2, 1, 1, 0., 1.e10, 'seaside_onshore.tt2'])

    # == setdtopo.data values ==
    dtopo_data = rundata.dtopo_data
    # for moving topography, append lines of the form :   (<= 1 allowed for now!)
    #   [topotype, minlevel,maxlevel,fname]

    # == setqinit.data values ==
    #rundata.qinit_data.qinit_type = 4
    rundata.qinit_data.qinitfiles = []
    # for qinit perturbations, append lines of the form: (<= 1 allowed for now!)
    #   [minlev, maxlev, fname]

    # == fgmax.data values ==
    fgmax_files = rundata.fgmax_data.fgmax_files
    # for fixed grids append to this list names of any fgmax input files
    #fgmax_files.append('fgmax_grid.txt')
    #rundata.fgmax_data.num_fgmax_val = 5  # Save h,s,hs,hss,min_depth


    return rundata
    # end of function setgeo
    # ----------------------



if __name__ == '__main__':
    # Set up run-time parameters and write all data files.
    import sys
    rundata = setrun(*sys.argv[1:])
    rundata.write()

