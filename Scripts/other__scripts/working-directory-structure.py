# GPW Design Working Directory
# Creates structure of working directory.

# Import Python Libraries
import arcpy, os, sys
from arcpy import env

# Set Overwrite Output Environment
env.overwriteOutput = 1

oldCensus = r'\\DATASERVER0\gpw\GPW4\Working\Census'

newWorking = r'\\DATASERVER0\gpw\GPW4\Working\COUNTRY' + os.sep

env.workspace = oldCensus

workspaceList = arcpy.ListWorkspaces("*")
workspaceList.sort()

for workspace in workspaceList:
    print workspace
    isoCode = workspace[-3:]
    if isoCode == "xls":
        pass
    elif isoCode == "ies":
        pass
    else:
        newISO = newWorking + isoCode
        if arcpy.Exists(newISO) == True:
            print newISO + " already exists"
        else:
            os.mkdir(newISO)
            print "Created directory for " + isoCode
            newCensus = newISO + os.sep + "census"
            newBoundary = newISO + os.sep + "boundary"
            newMerge = newISO + os.sep + "merge"
            os.mkdir(newCensus)
            print "Created directory for " + newCensus
            os.mkdir(newBoundary)
            print "Created directory for " + newBoundary
            os.mkdir(newMerge)
            print "Created directory for " + newMerge
