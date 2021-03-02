1. The gFoamEXE generates an executable file gFoamEXE.out
2. gFoamEXE.out is an openFoam solver for advection-diffusion problem.
3. To generate gFoamEXE.out, modify the directory in .gFoamEXE/Make/files, then run wmake.
4. To use gFoamEXE.out, put it into an openFoam project and run it.

Note that the solver is developed based on a standard solver "buoyantBoussinesqPimpleFoam". There may be some redundant variables.

Originally developed by Bowen Ling, modified by Ziyan Wang.

