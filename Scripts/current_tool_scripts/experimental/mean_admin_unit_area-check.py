# Kytt MacManus
# April 14 2014
# Produce Mean Area Unit Grids

##  From GPW3 Documentation:
##    Because countries vary between each other and internally on the size of the
##    administrative areas, analysis of the data may benefit from more information about the
##    administrative area underlying each unit in the output grid. Thus, for GPW version 3 we
##    constructed a population-weighted administrative unit area layer. This layer allows the
##    determination, on a pixel-by-pixel basis, of the mean administrative unit area that was
##    used as an input for the population count and density grids. For grid cells (pixels) that
##    are wholly comprised of one input unit, the output value is the total area of the input
##    unit. Where grid cells are comprised of multiple input units, the output value is the
##    population-weighted mean of all of the inputs.


# Import libraries
import arcpy, os, sys, datetime
runTime = datetime.datetime.now()
# Define workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'
# Check out Spatial Analyst License
arcpy.CheckOutExtension("SPATIAL")
# Set workspace environment
arcpy.env.workspace = workspace

# List File GDBs
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

# Iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    meanList = arcpy.ListRasters("*mean*admin*")

    if len(meanList)<>1:
        print "Mean Area for " + gdb

    numList = arcpy.ListRasters("*num*input*")
    if len(numList)<>1:
        print "Num Inputs for " + gdb
