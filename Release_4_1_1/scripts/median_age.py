#Jane Mills
#Median age

import arcpy, os, numpy

inFolder = r'\\Dataserver1\gpw\GPW4\Release_411\data\rasters_30sec'
outFolder = r'\\Dataserver1\gpw\GPW4\Release_411\cartographic\mxds_data\median_age'

arcpy.env.workspace = inFolder
rList = arcpy.ListRasters("*a0*bt*cntm*")
rList.sort()
rList = [rList[0]]+rList[2:5]+rList[7:16]+[rList[17]]

lls = [arcpy.Point(-180,0),arcpy.Point(-90,0),arcpy.Point(0,0),arcpy.Point(90,0),
       arcpy.Point(-180,-90),arcpy.Point(-90,-90),arcpy.Point(0,-90),arcpy.Point(90,-90)]

for j in range(1,8):
    print("working on tile {}".format(j))
    ageRasters = numpy.zeros((10800,10800,14))
    cumFreq = numpy.zeros((10800,10800,14))
    
    ll = lls[j]
    
    for i in range(len(rList)):
        r = rList[i]
        ageRasters[:,:,i] = arcpy.RasterToNumPyArray(r, ll, 10800, 10800, nodata_to_value = 0)
        cumFreq[:,:,i] = numpy.sum(ageRasters,axis = 2)
    
    totalPop = numpy.divide(cumFreq[:,:,13],2)
    totalPop = numpy.repeat(totalPop[:,:,numpy.newaxis], 14, axis=2)
    middleGroup = cumFreq >= totalPop
    middleIndex = numpy.argmax(middleGroup, axis = 2)
    l = middleIndex*5
    F = middleIndex - 1
    F[F<0] = 0
    FF = numpy.zeros((10800,10800))
    
    for i in range(0,numpy.max(F)+1):
        FF[F == i] = cumFreq[F == i,i]
    
    f = middleIndex
    ff = numpy.zeros((10800,10800))
    for i in range(0,numpy.max(f)+1):
        ff[f == i] = ageRasters[f == i,i]
    
    i = 5
    med = numpy.zeros((10800,10800))
    med[ff > 0] = l[ff>0] + (totalPop[ff>0,0]-FF[ff>0])*i/ff[ff>0]
    med[med < 0] = 0
    
    cellx = arcpy.GetRasterProperties_management(r,"CELLSIZEX")
    celly = arcpy.GetRasterProperties_management(r,"CELLSIZEY")
    newRast = arcpy.NumPyArrayToRaster(med, ll, float(cellx.getOutput(0)), float(celly.getOutput(0)), 0)
    outRast = os.path.join(outFolder,"median_age_"+str(j+1)+".tif")
    newRast.save(outRast)
    
    cs = arcpy.Describe(r).spatialReference
    arcpy.DefineProjection_management(outRast, cs)


