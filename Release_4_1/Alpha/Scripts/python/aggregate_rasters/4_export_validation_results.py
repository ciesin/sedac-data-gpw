#Jane Mills
#7/12/16
#GPW
#Validate the grids

import arcpy, os, csv
from arcpy import env

arcpy.CheckOutExtension("Spatial")

def export(resolution):
    inRoot = r'F:\GPW\aggregate_rasters\rasters_other_resolution'
    inGDB = os.path.join(inRoot,resolution,'validation.gdb')

    env.workspace = inGDB
    tList = arcpy.ListTables()

    outTable = os.path.join(inRoot,'counts_'+resolution+'.csv')
    cfields = ['Country','grid','SUM']

    with open(outTable,'w',newline='') as f:
        writer = csv.writer(f,delimiter =",",quoting=csv.QUOTE_MINIMAL)
        writer.writerow(cfields)
        for t in tList:
            if 'population_count' in t:
                with arcpy.da.SearchCursor(t,['Value','SUM']) as cursor:
                    for row in cursor:
                        writer.writerow([row[0],t,row[1]])
            else:
                pass
            

export('0_25_degree')
print("finished 0.25 degree")

export('0_5_degree')
print("finished 0.5 degree")

export('1_degree')
print("finished 1 degree")

export('2_5_minute')
print("finished 2.5 minute")
