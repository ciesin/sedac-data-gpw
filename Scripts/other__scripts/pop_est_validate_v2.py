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
ISO = 'mli'#arcpy.GetParameterAsText(0)
country_estimate = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\mli.gdb\mli_estimates'#arcpy.GetParameterAsText(1)

gpw_e = []
un_e = []
gpw_total = 0
un_total = 0
internal_vld = {}

fields = arcpy.ListFields(country_estimate)

#iterating lists to determine the fields that needed to be validated
for field in arcpy.ListFields(country_estimate):
    if field.name.startswith("E_"):
        gpw_e.append(field.name)
    elif field.name.startswith("UNE_"):
        un_e.append(field.name)

gpw_e.sort()
un_e.sort()
est_cursor = arcpy.SearchCursor(country_estimate)

##for est in est_cursor:
##    temp = []
##    for gpw, un in zip(gpw_e, un_e):
##        if abs(est.getValue(gpw) - est.getValue(un))> 1000:
##            temp.append([gpw, est.getValue(gpw) - est.getValue(un)])
##    if len(temp)> 0:
##        internal_vld.update({est.getValue("USCID"):temp})

##est_cursor.reset()
for gpw, un in zip(gpw_e, un_e):
    est_cursor = arcpy.SearchCursor(country_estimate)
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

#create a report .csv file with the boundary field name and asscociated file name
##with open(r"\\Dataserver0\gpw\GPW4\Gridding\validation_report\{0}_report.csv".format(ISO), "wb") as report_f:
##    report_w = csv.writer(report_f, delimiter = ',')
##    for key, value in internal_vld.iteritems():
##        report_w.writerow([key.encode('utf-8'), value])
if len(internal_vld) > 0:
     arcpy.AddMessage("Generating Report for estimate table!")
     with open(r"\\Dataserver0\gpw\GPW4\Gridding\validation_report\{0}__internal_report.csv".format(ISO), "wb") as report_f:
        report_w = csv.writer(report_f, delimiter = ',')
        for key, value in internal_vld.iteritems():
            for each in value:
                ##arcpy.AddMessage("{0}{1}{2}".format(key, each[0], each[1]))
                report_w.writerow([key.encode('utf-8'), each[0].encode('utf-8'), each[1]])