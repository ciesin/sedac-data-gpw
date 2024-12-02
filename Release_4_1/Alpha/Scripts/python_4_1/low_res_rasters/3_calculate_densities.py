#Jane Mills
#4/17/2017
#GPW
#Divide the counts by the land area to get the densities

import arcpy, os
from arcpy import env

arcpy.CheckOutExtension("Spatial")

outFolder = r'D:\gpw\release_4_1\low_res'

env.workspace = outFolder

resolutions = ['2pt5_min','15_min','30_min','1_deg']

for res in resolutions:
    rList1 = arcpy.ListRasters("*_e_a0*"+res+"*")
    rList2 = arcpy.ListRasters("*_e_atotpopm*"+res+"*")
    rList3 = arcpy.ListRasters("*_e_atotpopf*"+res+"*")
    
    rList = rList1 + rList2 + rList3
    rList.sort()
    land = arcpy.ListRasters("*_maskedareakm*"+res+"*")[0]

    for r in rList:
        print r
        outR = r.replace('_cntm_','_dens_')
        arcpy.gp.Divide_sa(r,land,outR)


