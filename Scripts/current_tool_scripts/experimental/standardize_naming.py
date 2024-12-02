# Kytt MacManus
# July 8, 2014

# Import Libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

### define csv file
##attributes =r'\\Dataserver0\gpw\GPW4\Gridding' + os.sep + 'inventory_v3.csv'
### open csv file and write header
##csvFile = csv.writer(open(attributes,'wb'))
##csvFile.writerow(("COUNTRYCODE","ADMINLEVEL","INPUTBOUNDARIES","NUMINPUTFEATURES"
##                  ,"FISHNET",
##                  "FISHNETVARIABLES","ESTIMATES","WATERMASK","UNADJUSTMENT",
##                  "AGGREGATEDESTIMATES","INTERSECT","PROPORTIONS",
##                  "PROPORTIONVARIABLES","GROWTHRATE"))

# iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    COUNTRYCODE = os.path.basename(gdb)[:-4]
    # Grab CENSUSTABLE
    censusTables = arcpy.ListTables("*input_population")
    if len(censusTables)==0:
        print "There is a missing census table in:  " + gdb
        continue
    else:
        for censusTable in censusTables:
            
    
    
##    fcs = arcpy.ListFeatureClasses("*boundaries_2010")
##    if len(fcs)==0:
##        print gdb + " has something missing"
##    else:
##        for fc in fcs:
##            # test for lock
##            schemaLock = arcpy.TestSchemaLock(fc)            
##            ADMINLEVEL = fc.split("_")[1][-1]
##            # Check for INPUTBOUNDARIES
##            if arcpy.Exists(fc + "_gridding"):
##                INPUTBOUNDARIES = "1"
##            else:
##                INPUTBOUNDARIES = "0"
##            # Count number of features in INPUTBOUNDARIES
##            NUMINPUTFEATURES = arcpy.GetCount_management(fc + "_gridding")[0]
##            # Check for FISHNET
##            # Can add logic to characterize FISHNETVARIABLES later
##            if arcpy.Exists(COUNTRYCODE + "_fishnet"):
##                FISHNET = "1"
##                FISHNETVARIABLES = str(len(arcpy.ListFields(COUNTRYCODE + "_fishnet","SUM*")))
##            else:
##                FISHNET = "0"
##                FISHNETVARIABLES = "0"                                    
##                                           
##            # Check for ESTIMATES 
##            if arcpy.Exists(COUNTRYCODE + "_estimates"):
##                ESTIMATES = "1"
##            else:
##                ESTIMATES = "0"
##            # Check for WATERMASK 
##            if arcpy.Exists(COUNTRYCODE + "_water_mask"):
##                WATERMASK = "1"
##            else:
##                WATERMASK = "0"
##            # Check for UNADJUSTMENT 
##            if arcpy.Exists(COUNTRYCODE + "_un_adjustment"):
##                UNADJUSTMENT = "1"
##            else:
##                UNADJUSTMENT = "0"
##            # Check for AGGREGATEDESTIMATES
##            if arcpy.Exists(fc + "_aggregated_estimates"):
##                AGGREGATEDESTIMATES = "1"
##            else:
##                AGGREGATEDESTIMATES = "0"
##            # Check for INTERSECT
##            if arcpy.Exists(fc + "_fishnet_clipped_intersect"):
##                INTERSECT = "1"
##            else:
##                INTERSECT = "0"
##            # Check for PROPORTIONS
##            # Insert additional logic later to characterize propFields
##            # Possibly also rename here
##            propFile = arcpy.ListTables("*proportions*")
##            if len(propFile) ==0:
##                PROPORTIONS = "0"
##                PROPORTIONVARIABLES = "0"
##            else:
##                propFile = propFile[0]
##                PROPORTIONS = "1"
##                propFields = arcpy.ListFields(propFile,"*PROP")
##                if len(propFields) ==0:
##                    PROPORTIONVARIABLES = "0"
##                else:
##                    PROPORTIONVARIABLES = str(len(propFields))
##                
##            # Check for GROWTHRATE
##            # Possibly also rename here
##            agrFile = arcpy.ListTables("*growth*")
##            if len(agrFile) ==0:
##                GROWTHRATE = "0"
##            else:
##                GROWTHRATE = "1"
##        
##
##            csvFile.writerow((COUNTRYCODE,ADMINLEVEL,INPUTBOUNDARIES,
##                  NUMINPUTFEATURES,FISHNET,FISHNETVARIABLES,ESTIMATES,WATERMASK,UNADJUSTMENT,
##                  AGGREGATEDESTIMATES,INTERSECT,PROPORTIONS,
##                  PROPORTIONVARIABLES,GROWTHRATE))
##
##

                

    
    
print datetime.datetime.now() - startTime
