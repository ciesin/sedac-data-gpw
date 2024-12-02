import arcpy, os
from arcpy import env

sde = r'Database Connections\sde.sde'

env.workspace = sde

fdList = arcpy.ListDatasets("*USA_*")
fdList.sort()

for fd in fdList:
    print fd

    env.workspace = os.path.join(sde,fd)
    fc = arcpy.ListFeatureClasses()[0]
    fcPath = os.path.join(sde,fd,fc)
    
    arcpy.AssignDomainToField_management(fcPath,"BOUNDARY_CONTEXT","boundary_context")
    arcpy.AssignDomainToField_management(fcPath,"ATOTPOP","population_count_range")
    arcpy.AssignDomainToField_management(fcPath,"E_ATOTPOPBT_2000","population_count_range")
    arcpy.AssignDomainToField_management(fcPath,"E_ATOTPOPBT_2005","population_count_range")
    arcpy.AssignDomainToField_management(fcPath,"E_ATOTPOPBT_2010","population_count_range")
    arcpy.AssignDomainToField_management(fcPath,"E_ATOTPOPBT_2015","population_count_range")
    arcpy.AssignDomainToField_management(fcPath,"E_ATOTPOPBT_2020","population_count_range")
    arcpy.AssignDomainToField_management(fcPath,"RPOPYEAR","year_range")

    print "assigned domains"

print "done"
