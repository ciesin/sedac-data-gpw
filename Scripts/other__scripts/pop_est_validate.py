'''
Validation of population estimates for GPW4 project.
The function of this script is using the matched boundary file of
one country to do zonal statistics for CIESIN estimates and UN estimates,
then compare the differences between SUM field in the outcome table.
If there is over 1000 differences in between the values then the estimates
should be adjusted.

@Author: Ian Chenyang Zhao
'''

'''import modules'''
import os, csv, itertools, arcpy
from arcpy import env
from arcpy.sa import *

# Set local variables
ISO = arcpy.GetParameterAsText(0)
zonal_shp =  arcpy.GetParameterAsText(1)
zonal_field = arcpy.GetParameterAsText(2)
rst_db =  arcpy.GetParameterAsText(3)
estimates_tb = arcpy.GetParameterAsText(4)

# Set environment settings
env.workspace = rst_db
env.overwriteOutput = True

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

#get lists of GPW estimates files' name and UN estimates files' name, using wildcard "_E_" and "_UNE_", defininig other variables.
gpw_l = arcpy.ListRasters("*_E_*", "GRID")
un_l = arcpy.ListRasters("*_UNE_*", "GRID")
report = {}
gpw_e = []
un_e = []
gpw_total = 0
un_total = 0
internal_vld = {}


#sort lists before comparison
gpw_l.sort()
un_l.sort()

#getting the iteration limits from the length of each list, length of two list should be identical, otherwise we should throw an error.
num = len(gpw_l)
i = 0

#internal validation GPW estimation against UN estimation for each boundary under each census information, such as ATOTPOPBT/ATOTPOPMT..etc.
for field in arcpy.ListFields(estimates_tb):
    if field.name.startswith("E_"):
        gpw_e.append(field.name)
    elif field.name.startswith("UNE_"):
        un_e.append(field.name)

#sort list before retriveing values to keep consistency between the comparison two estimates
gpw_e.sort()
un_e.sort()

#interating throung ISO_estimate table to do internal validation and cross validation on estimation from GPW and UN
for gpw, un in zip(gpw_e, un_e):
    est_cursor = arcpy.SearchCursor(estimates_tb)
    gpw_total = 0
    un_total = 0
    temp = []
    for est in est_cursor:
        if abs(est.getValue(gpw) - est.getValue(un)) > 1000:
            temp.append([est.getValue("USCID"),est.getValue(gpw) - est.getValue(un)])
            internal_vld.update({gpw : temp})
        gpw_total = gpw_total + est.getValue(gpw)
        un_total = un_total + est.getValue(un)
    print gpw_total, un_total, gpw
    print "%s, Country Level Difference between GPW estimates and UN estimates is %f \n"%(gpw,gpw_total - un_total)

# Doing zonalstatistics and exported as a table
while i < num:
    #setting working environment to raster folders
    env.workspace = rst_db
    #doing zonal statistics
    arcpy.AddMessage("Calculating Zonal Statistics #{0}!".format(i+1))
    ZonalStatisticsAsTable(zonal_shp,"{0}".format(zonal_field),"{0}".format(gpw_l[i])\
                                           ,r"{0}\_E_".format(env.scratchGDB),"NODATA",'ALL')
    ZonalStatisticsAsTable(zonal_shp,"{0}".format(zonal_field),"{0}".format(un_l[i])\
                                           ,r"{0}\_UNE_".format(env.scratchGDB),"NODATA",'ALL')
    #switch working environment folder to temp geodatabase
    env.workspace = env.scratchGDB
    gpw_cursor = arcpy.SearchCursor("_E_", fields = "SUM, {0}".format(zonal_field), sort_fields = "{0}".format(zonal_field))
    un_cursor = arcpy.SearchCursor("_UNE_",fields = "SUM, {0}".format(zonal_field),sort_fields = "{0}".format(zonal_field))
    #compare the sum between GPW estimates and UN estimates
    #if the absolute value of the differences is larger than 1000 than print admin area name and file name of the gpw estimates
    for gpw_row, un_row in zip(gpw_cursor, un_cursor):
        diff = gpw_row.SUM - un_row.SUM
        if abs(diff) > 1000:
            report.update({gpw_l[i]:[gpw_row.getValue(zonal_field), diff]})
    i += 1

arcpy.AddMessage("{0} records are mismatched".format(len(report)))
#create a report .csv file with the boundary field name and asscociated file name
#1
if len(internal_vld) > 0:
     arcpy.AddMessage("Generating Report for estimate table!")
     with open(r"\\Dataserver0\gpw\GPW4\Gridding\validation_report\{0}__internal_report.csv".format(ISO), "wb") as report_f:
        report_w = csv.writer(report_f, delimiter = ',')
        for key, value in internal_vld.iteritems():
            for each in value:
                report_w.writerow([key.encode('utf-8'), each[0].encode('utf-8'), each[1]])
#2
if len(report) > 0:
    arcpy.AddMessage("Generating Report for gridded layers!")
    with open(r"\\Dataserver0\gpw\GPW4\Gridding\validation_report\{0}__grid_report.csv".format(ISO), "wb") as report_f:
        report_w = csv.writer(report_f, delimiter = ',')
        for key, value in report.iteritems():
            arcpy.AddMessage("{0}{1}".format(key, value))
            report_w.writerow([key, value[0], value[1]])
else:
    arcpy.AddMessage("All validated!")
arcpy.AddMessage("Done!")  
