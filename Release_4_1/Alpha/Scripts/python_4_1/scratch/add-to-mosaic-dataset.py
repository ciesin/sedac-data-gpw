# Kytt MacManus
# 9-14-15
# merge_rasters.py

import arcpy, os, datetime, multiprocessing, socket
     
def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    host = socket.gethostname()
    if host == 'Devsedarc3':
        inWS = r'F:\gpw\release_4_1\country_tifs'
    elif host == 'Devsedarc4':
        inWS = r'D:\gpw\release_4_1\country_tifs'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    rasterLists = []
    folders = arcpy.ListWorkspaces("usa*","Folder")
    for folder in folders:
        arcpy.env.workspace = folder
        subfolders = arcpy.ListWorkspaces("*","Folder")
        templateFolder = subfolders[0]
        rootName = os.path.basename(templateFolder).upper()   
        arcpy.env.workspace = templateFolder
        rasters = arcpy.ListRasters("*_E_ATOTPOPBT*2010*")
        # grab the wildcard
        for raster in rasters:
            
            inRasters = []
            wildCard = raster.replace(rootName,"")
            # cycle the subfolders and assemble the rasters
            for subfolder in subfolders:
                inRaster = subfolder + os.sep + os.path.basename(subfolder).upper() + wildCard
                inRasters.append(inRaster)
            rasterLists.append(inRasters)

    rasterList = rasterLists[0]
    mos = r'F:\gpw\release_4_1\country_tifs\usa_test.gdb\ustotpop2010'
    arcpy.AddRastersToMosaicDataset_management(mos,"Raster Dataset",rasterList)
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
