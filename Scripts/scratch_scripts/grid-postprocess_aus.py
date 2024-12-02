# import libraries
import arcpy, os, sys
import datetime


startTime = datetime.datetime.now()
    
# define inputs
inFC = r'D:\GPW\aus\aus.gdb\aus_admin5_boundaries_2010'
##inFC = arcpy.GetParameterAsText(0)
##workspace = arcpy.GetParameterAsText(1)
workspace = r'D:\GPW\aus\aus.gdb'
waterExist = "true"#arcpy.GetParameterAsText(2)

# define workspace environment
arcpy.env.workspace = workspace

# define gridding resolution
# Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
# 1 degree divided into 120 parts is 30 seconds
linespd = 120
##linespd = arcpy.GetParameterAsText(1)

# parse inFC to determine rootName
rootName = os.path.basename(inFC)[:3]

# define input fishnet
inFish = rootName + "_fishnet"

# check to see that fishnet exists, if it doesn't kill the script
if not arcpy.Exists(inFish):
    arcpy.AddMessage("The input fishnet does not exist, check the geodatabase")
    sys.exit("The input fishnet does not exist, check the geodatabase")

# define estimatesTable
estimatesTable = rootName + "_estimates"

# Create In_memory Fishnet
fishnet = "in_memory" + os.sep + rootName + "_fishnet"
try:
    addTime = datetime.datetime.now()
    arcpy.CopyFeatures_management(inFish, fishnet)
    print "Created " + fishnet
    print datetime.datetime.now() - addTime
except:
    print arcpy.GetMessages()

# copy in_memory version back to disk
outFish = rootName + "_fishnet_v2"
try:
    addTime = datetime.datetime.now()
    arcpy.CopyFeatures_management(fishnet, outFish)
    arcpy.Delete_management(fishnet)
    print "Created " + outFish
    print datetime.datetime.now() - addTime
except:
    print arcpy.GetMessages()

    print datetime.datetime.now() - startTime
if __name__ == '__main__':
    main()
