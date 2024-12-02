# multiprocess_create_custom_prjs
# create localized mollweide projections per country for gridding algorithm
# executed on DEVSEDARC4
import os
import multiprocessing
import arcpy
 
def create_projection(fc):
    # describe the fc
    desc = arcpy.Describe(fc)
    # get extent
    extent = desc.Extent
    # get central meridian
    xctr = round(((extent.XMax + extent.XMin) / 2.0), 1)
    # add logic to control for if range is greater than 180, it may cross hemispheres and should not
    # be processed as such
    if abs(extent.XMax - extent.XMin) > 180.0:
        errorFile = r'D:\gpw\custom_projections' + os.path.sep + os.path.basename(fc)[:3] + "_error.txt"
        with open(errorFile,'w')as error:
            error.write(" ERROR \n")
    else:
        # Define output projection file
        prjFile = r'D:\gpw\custom_projections' + os.path.sep + os.path.basename(fc)[:3] + "_fishnet_mollweide.prj"
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
    workspace = r'D:\gpw\release_4_1\input_data\country_boundaries_hi_res.gdb'
    arcpy.env.workspace = workspace
    fcs = arcpy.ListFeatureClasses("umi*")
    print "processing"
    for fc in fcs:
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
