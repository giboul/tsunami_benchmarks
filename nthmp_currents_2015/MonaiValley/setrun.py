""" 
Module to set up run time parameters for Clawpack.

The values set in the function setrun are then written out to data files
that will be read in by the Fortran code.
    
""" 
#changed by VL 29042015 to work with GeoClaw v.5.2.2

import os
import numpy as np

try:
    CLAW = os.environ['CLAW']
except:
    raise Exception("*** Must first set CLAW enviornment variable")

# Scratch directory for storing topo and dtopo files:
scratch_dir = os.path.join(CLAW, 'geoclaw', 'scratch','cascais_all')


#------------------------------
def setrun(claw_pkg='geoclaw'):
#------------------------------
    
    """ 
    Define the parameters used for running Clawpack.

    INPUT:
        claw_pkg expected to be "geoclaw" for this setrun.

    OUTPUT:
        rundata - object of class ClawRunData 
    
    """ 
    
   
    from clawpack.clawutil import data 

    assert claw_pkg.lower() == 'geoclaw',  "Expected claw_pkg = 'geoclaw'"

    num_dim = 2
    rundata = data.ClawRunData(claw_pkg, num_dim)


    #------------------------------------------------------------------
    # Problem-specific parameters to be written to setprob.data:
    #------------------------------------------------------------------
    
    #probdata = rundata.new_UserData(name='probdata',fname='setprob.data')


    #------------------------------------------------------------------
    # GeoClaw specific parameters:
    #------------------------------------------------------------------
    rundata = setgeo(rundata)   # Defined below
    
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
    clawdata.lower[0] = 0.
    clawdata.upper[0] = 5.48800e+00  
    
    clawdata.lower[1] = 0.
    clawdata.upper[1] = 3.40200e+00    

    # Number of grid cells:
    clawdata.num_cells[0] = 423
    clawdata.num_cells[1] = 243
        

    # ---------------
    # Size of system:
    # ---------------

    # Number of equations in the system:
    #clawdata.meqn = 3
    clawdata.num_eqn = 3

    # Number of auxiliary variables in the aux array (initialized in setaux)
    #clawdata.maux = 3
    clawdata.num_aux = 3    

    # Index of aux array corresponding to capacity function, if there is one:
    #clawdata.mcapa = 0
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
    clawdata.restart_file = 'fort.chk00036'  # File to use for restart data

    # -------------
    # Output times:
    #--------------

    # Specify at what times the results should be written to fort.q files.
    # Note that the time integration stops after the final output time.
    # The solution at initial time t0 is always written in addition.

    #clawdata.outstyle = 2
    clawdata.output_style = 2


    if clawdata.output_style==1:
        # Output nout frames at equally spaced times up to tfinal:
        clawdata.num_output_times = 60
        clawdata.tfinal = 30.0
        clawdata.output_t0 = True  # output at initial (or restart) time?


    elif clawdata.output_style == 2:
        # Specify a list of output times.  
        import numpy
        clawdata.output_times =  list(numpy.linspace(14.25,25,44))    
        clawdata.output_times =  list(numpy.linspace(0,50,100))     
        clawdata.num_output_times = len(clawdata.output_times)


    elif clawdata.output_style == 3:
        # Output every iout timesteps with a total of ntot time steps:
        clawdata.output_step_interval = 1
        clawdata.total_steps = 20
        clawdata.output_t0 = True 


    clawdata.output_format = 'ascii'      # 'ascii' or 'netcdf' 

    clawdata.output_q_components = 'all'   # need all
    clawdata.output_aux_components = 'none'  # eta=h+B is in q
    clawdata.output_aux_onlyonce = False    # output aux arrays each frame


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
    clawdata.dt_variable = 1
    
    # Initial time step for variable dt.  
    # If dt_variable==0 then dt=dt_initial for all steps:
    clawdata.dt_initial = 0.001
    
    # Max time step to be allowed if variable dt used:
    clawdata.dt_max = 1e+99
    
    # Desired Courant number if variable dt used, and max to allow without 
    # retaking step with a smaller dt:
    clawdata.cfl_desired = 0.9
    clawdata.cfl_max = 1.0
    
    # Maximum number of time steps to allow between output times:
   # clawdata.max_steps = 50000
    clawdata.steps_max = 50000

    
    

    # ------------------
    # Method to be used:
    # ------------------

    # Order of accuracy:  1 => Godunov,  2 => Lax-Wendroff plus limiters
    clawdata.order = 2
    
    # Use dimensional splitting? (not yet available for AMR)
    clawdata.dimensional_split = 'unsplit'
    
    
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
    #clawdata.mbc = 2
    clawdata.num_ghost = 2
    
    # Choice of BCs at xlower and xupper:
    #   0 => user specified (must modify bcN.f to use this option)
    #   1 => extrapolation (non-reflecting outflow)
    #   2 => periodic (must specify this at both boundaries)
    #   3 => solid wall for systems where q(2) is normal velocity
    
   
    clawdata.bc_lower[0] = 0
    clawdata.bc_upper[0] = 1

    clawdata.bc_lower[1] = 1
    clawdata.bc_upper[1] = 1


    # --------------
    # Checkpointing:
    # --------------

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
    #mxnest = 1
   # amrdata.amr_levels_max = 3
    amrdata.amr_levels_max = 1

    #clawdata.mxnest = -mxnest   # negative ==> anisotropic refinement in x,y,t
    #amrdata.amr_levels_max = -amrdata.amr_levels_max   # negative ==> anisotropic refinement in x,y,t


    # List of refinement ratios at each level (length at least mxnest-1)
    amrdata.refinement_ratios_x = [4,4,4]
    amrdata.refinement_ratios_y = [4,4,4]
    amrdata.refinement_ratios_t = [4,4,4]

    # Specify type of each aux variable in amrdata.auxtype.
    # This must be a list of length maux, each element of which is one of:
    #   'center',  'capacity', 'xleft', or 'yleft'  (see documentation).

    amrdata.aux_type = ['center','center','yleft']


    # Flag using refinement routine flag2refine rather than richardson error
    #clawdata.tol = -1.0     # negative ==> don't use Richardson estimator
    amrdata.flag_richardson = False    # use Richardson?
    amrdata.flag2refine = True

    # steps to take on each level L between regriddings of level L+1:
    #clawdata.kcheck = 3     # how often to regrid (every kcheck steps)
    amrdata.regrid_interval = 3

    # width of buffer zone around flagged points:
    # (typically the same as regrid_interval so waves don't escape):
    #clawdata.ibuff  = 2     # width of buffer zone around flagged points
    amrdata.regrid_buffer_width  = 2


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
    amrdata.tprint = False       # time step reporting each level
    amrdata.uprint = False      # update/upbnd reporting
    

    # More AMR parameters can be set -- see the defaults in pyclaw/data.py

    # ---------------
    # Regions:
    # ---------------
    # == setregions.data values ==
    #geo_data.regions = []
    rundata.regiondata.regions = []
    # to specify regions of refinement append lines of the form
    #  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]
    rundata.regiondata.regions.append([1,1,0.,1e10,1.,6.,0,4.])
    rundata.regiondata.regions.append([1,2,0.,1e10,3.,6.,0,4.])



    # ---------------
    # Gauges:
    # ---------------
    gauge_names = ['0','5','7','9']
    # == setgauges.data values ==
    #geo_data.gauges = []
    rundata.gaugedata.gauges = []
    # for gauges append lines of the form  [gaugeno, x, y, t1, t2]
    rundata.gaugedata.gauges.append([0, 0.2, 2.7, 0., 1.e10])
    rundata.gaugedata.gauges.append([5, 4.521, 1.196, 0., 1.e10])
    rundata.gaugedata.gauges.append([7, 4.521, 1.696, 0., 1.e10])
    rundata.gaugedata.gauges.append([9, 4.521, 2.196, 0., 1.e10])

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
    # == setgeo.data values ==
    geo_data.gravity = 9.81
    geo_data.coordinate_system = 1
    geo_data.earth_radius = 6367.5e3

    # == Forcing Options
    geo_data.coriolis_forcing = False

    # == Algorithm and Initial Conditions ==
    geo_data.sea_level = 0.
    geo_data.dry_tolerance = 1.e-4
    geo_data.friction_forcing = False
    geo_data.manning_coefficient = 0. 
    geo_data.friction_depth = 20.

    # Refinement settings
    refinement_data = rundata.refinement_data
    refinement_data.variable_dt_refinement_ratios = False  
    refinement_data.wave_tolerance = 1.e-2 
    refinement_data.deep_depth = 1.e2 
    refinement_data.max_level_deep = 3 


    # == settopo.data values ==
    #geo_data.topofiles = []
    topo_data = rundata.topo_data                 
    # for topography, append lines of the form
    #   [topotype, minlevel, maxlevel, t1, t2, fname]
    topo_data.topofiles.append([2, 1, 1, 0., 1.e10, 'MonaiValley.tt2'])

    # == setdtopo.data values ==
    #geo_data.dtopofiles = []
    #dtopo_data = rundata.dtopo_data       #changed VL 29042015
    #geo_data.dtopofiles = []
    # for moving topography, append lines of the form:  (<= 1 allowed for now!)
    #   [minlevel,maxlevel,fname]

    # == setqinit.data values ==
    #geo_data.iqinit = 0 
    rundata.qinit_data.qinit_type = 0       
    rundata.qinit_data.qinitfiles = []  

    # for qinit perturbations, append lines of the form: (<= 1 allowed for now!)
    #   [minlev, maxlev, fname]
    #geo_data.qinitfiles.append([1, 2, 'wave.xyz'])

    # == setfixedgrids.data values ==
    #geo_data.fixedgrids = []
    # fixed_grids = rundata.fixed_grid_data         
    # for fixed grids append lines of the form
    # [t1,t2,noutput,x1,x2,y1,y2,xpoints,ypoints,\
    #  ioutarrivaltimes,ioutsurfacemax]

    return rundata
    # end of function setgeo
    # ----------------------



if __name__ == '__main__':                      
    # Set up run-time parameters and write all data files.           
    import sys
    if len(sys.argv) == 2:
        rundata = setrun(sys.argv[1])
    else:
        rundata = setrun()

    rundata.write()
