# Create a NewSource folder, with the folders rearranged to our new folder
# structure

# Ensure you have already created a dupliate Source folder
#(run 1CopyFolderContents.py)

# Import Python Libraries
import arcpy, os, sys, shutil
from arcpy import env

python = "C:\Users\edwhitfi\Desktop\Python"
boundary = "C:\Users\edwhitfi\Desktop\Python\Source\Boundary\Country"
census = "C:\Users\edwhitfi\Desktop\Python\Source\Census"
rearrangedSource = "C:\Users\edwhitfi\Desktop\Python\RearrangedSource\Country"

# Copy boundary files to new folder structure
env.workspace = boundary

workspaceList = arcpy.ListWorkspaces("*")
workspaceList.sort()

print "Boundary folders and files have been copied to the RearrangedSource folder for the following countries:"
for workspace in workspaceList:
    isoCode = workspace[-3:]
    newIsoBoundary = rearrangedSource + os.sep + isoCode + os.sep + "boundary"
    try:
        shutil.copytree(workspace,newIsoBoundary)
        print isoCode 
    except IOError:
        print "Files already exist"

# Copy census files to new folder structure
env.workspace = census

workspaceList = arcpy.ListWorkspaces("*")
workspaceList.sort()

print "Census folders and files have been copied to the RearrangedSource folder for the following countries:"
for workspace in workspaceList:
    isoCode = workspace[-3:]
    newIsoCensus = rearrangedSource + os.sep + isoCode + os.sep + "census"
    try:
        shutil.copytree(workspace,newIsoCensus)
        print isoCode 
    except IOError:
        print "Files already exist"

# List countries missing either a boundary folder
env.workspace = rearrangedSource
print "The following countries are missing a boundary folder:"

workspaceList = arcpy.ListWorkspaces("*")
workspaceList.sort()

for workspace in workspaceList:
    isoCode = workspace[-3:]
    boundaryFolder = rearrangedSource + os.sep + isoCode + os.sep + "boundary"
    if arcpy.Exists(boundaryFolder) == True:
        pass
    else:
        print isoCode
            
# List countries missing either a census folder
env.workspace = rearrangedSource
print "The following countries are missing a census folder:"

workspaceList = arcpy.ListWorkspaces("*")
workspaceList.sort()

for workspace in workspaceList:
    isoCode = workspace[-3:]
    censusFolder = rearrangedSource + os.sep + isoCode + os.sep + "census"
    if arcpy.Exists(censusFolder) == True:
        pass
    else:
        print isoCode
        








