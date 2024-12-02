#Jane Mills
#8/5/2019
#Create census boundaries with data
#CLean up gridding boundaries (delete attributes)

import arcpy, os

inFolder = r'\\Dataserver1\gpw\GPW4\Release_411\data\boundaries\adjusted_boundaries_with_census_data'

boundaryGDB = os.path.join(inFolder,'originals.gdb')
outFolder = os.path.join(inFolder,'original_boundaries')

arcpy.env.workspace = boundaryGDB
fcList = arcpy.ListFeatureClasses()
fcList.sort()

inFC = fcList[0]
for inFC in fcList[1:]:
    iso = inFC[:3]
    print(iso)
    
    outGDB = os.path.join(outFolder,iso+'.gdb')
    if not os.path.exists(outGDB):
        arcpy.CreateFileGDB_management(outFolder,iso+'.gdb')
    
    outFC = os.path.join(outGDB,inFC+"_boundaries")
    arcpy.Copy_management(inFC,outFC)
    
    fList = [f.name for f in arcpy.ListFields(outFC) if not f.required]
    if len(fList) > 0:
        arcpy.DeleteField_management(outFC,fList)



