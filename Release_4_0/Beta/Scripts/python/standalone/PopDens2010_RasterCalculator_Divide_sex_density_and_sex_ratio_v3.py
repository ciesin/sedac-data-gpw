# Name: PopDens2010_RasterCalculator_Divide.py
# Description: Divides the values of two rasters on a cell-by-cell basis
# Requirements: Spatial Analyst Extension
# Olena and Erin 9-21-2015

# Import system modules
import arcpy, os
from arcpy import env
from arcpy.sa import *

# Set environment settings
workspace = r"\\Dataserver0\gpw\GPW4\Beta\Gridding\rasters"
env.workspace = workspace 

folderList = ["bra","can","grl","rus","usa"]
for folders in folderList:
    iso = folders
    print iso
    isogdb = workspace + os.sep + iso + os.sep + iso + ".gdb"
    env.workspace = isogdb
    iso = iso.upper()
  
   
   # Allow rasters to be overwritten
    arcpy.env.overwriteOutput = True


    # List area grid
    areaList = arcpy.ListRasters("*_AREAKMMASKED*","GRID")
    if len(areaList) == 0:
        print iso + " doesn't have an areaGrid"
        pass
    else:
        areaGrid = areaList[0]
        print "areaGrid = " + areaGrid

    # Calculate Female density grid
    # List female count grid 
        femaleList = arcpy.ListRasters("*_E_ATOTPOPFT_2010_CNTM","GRID")
        if len(femaleList) == 1:
            for female in femaleList:
                femaleGrid = female
                print "femaleGrid = " + femaleGrid
        elif len(femaleList) == 0:
            print "No FT_CNTM grid" 

    # Set up raster variables
        inRaster01 = Raster(femaleGrid)
        inRaster02 = Raster(areaGrid)           

    # Check out the ArcGIS Spatial Analyst extension license
        arcpy.CheckOutExtension("Spatial")

    # Execute Divide
        outDivide = inRaster01 / inRaster02
        femaleOutDivideName = iso + "_E_ATOTPOPFT_2010_DSM"


    # Save the output 
        outDivide.save(env.workspace + os.sep + femaleOutDivideName)
        print iso + " female density grid is done"


    # Calculate Male density grid
    # List male count grid 
        maleList = arcpy.ListRasters("*_E_ATOTPOPMT_2010_CNTM","GRID")
        if len(maleList) == 1:
            for male in maleList:
                maleGrid = male
                print "maleGrid = " + maleGrid
        elif len(maleList) == 0:
            print "No MT_CNTM grid" 

    # Set up raster variables
        inRaster03 = Raster(maleGrid)
        inRaster02 = Raster(areaGrid)           

    # Check out the ArcGIS Spatial Analyst extension license
        arcpy.CheckOutExtension("Spatial")

    # Execute Divide
        outDivide = inRaster03 / inRaster02
        maleOutDivideName = iso + "_E_ATOTPOPMT_2010_DSM"


    # Save the output 
        outDivide.save(env.workspace + os.sep + maleOutDivideName)
        print iso + "male density grid is done"


    #Calculate sex ratio

    # Set up raster variables
        inRaster03 = Raster(maleGrid)
        inRaster01 = Raster(femaleGrid)

    # Execute Divide
        outDivide = (inRaster03 / inRaster01)*100
        SexRatioOutDivideName = iso + "_E_2010_sex_ratio"
    # Save the output 
        outDivide.save(env.workspace + os.sep + SexRatioOutDivideName)
        print iso + "sex ratio grid is done"
        
    print "done"
        

