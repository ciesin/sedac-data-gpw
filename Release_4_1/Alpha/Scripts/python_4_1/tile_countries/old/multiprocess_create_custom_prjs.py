# multiprocess_create_custom_prjs
# create localized mollweide projections per country for gridding algorithm
# executed on DEVSEDARC3
import os
import multiprocessing
import arcpy
 
def create_projection(fc):
    name = fc.replace("_admin3_boundaries_2010_gridding","")
    name = name.replace("_admin5_boundaries_2010_gridding","")
    # describe the fc
    desc = arcpy.Describe(fc)
    # get extent
    extent = desc.Extent
    # get central meridian
    xctr = round(((extent.XMax + extent.XMin) / 2.0), 1)
    # add logic to control for if range is greater than 180, it may cross hemispheres and should not
    # be processed as such
    if abs(extent.XMax - extent.XMin) > 180.0:
        errorFile = r'F:\gpw\custom_projections' + os.path.sep + name + "_error.txt"
        with open(errorFile,'w')as error:
            error.write(" ERROR \n")
    else:
        # Define output projection file
        prjFile = r'F:\gpw\custom_projections' + os.path.sep + name + "_fishnet_mollweide.prj"
        if arcpy.Exists(prjFile):
            pass
        else:
        
            # Grab Projection Information from Global Mollweide
            mollweideIn = arcpy.SpatialReference(54009)
            # Export as string
            mollweideString = mollweideIn.exportToString()
            # Replace Central Meridian with xctr
            mollweideOut = mollweideString.replace("['Central_Meridian',0.0]","['Central_Meridian'," + str(xctr) + "]")
            # Write to custom prj file
            with open(prjFile,'w')as prj:
                prj.write(mollweideOut)
            print "Created " + prjFile
 
# End update_shapefiles
def main():
   
    # The number of jobs is equal to the number of files
##    workspace = r'E:\gpw\country\fishnets'
    workspace = r'F:\gpw\release_4_1\process'
    arcpy.env.workspace = workspace
    gdbs = arcpy.ListWorkspaces("*")
    for gdb in gdbs:
        arcpy.env.workspace = gdb
        fc = arcpy.ListFeatureClasses("*gridding")[0]    
        print fc
        create_projection(fc)
##    pool = multiprocessing.Pool()
##    pool.map(create_projection, gdb_list) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    # End main
    print "complete"
 
if __name__ == '__main__':
    main()
