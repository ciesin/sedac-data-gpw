# Kytt MacManus
# November 25, 2013

# import libraries
import arcpy, os, sys
import datetime



startTime = datetime.datetime.now()
clipnetInt = r'E:\gpw\bra\bra.gdb\bra_admin5_boundaries_fishnet_clipped_intersect'#arcpy.GetParameterAsText(0)
#r'E:\gpw\sen.gdb\sen_admin2_boundaries_2010_fishnet_clipped_intersect'
joinFeature = r'E:\gpw\bra\bra.gdb\bra_admin5_boundaries_water_mask_clipped_intersect_projected'#arcpy.GetParameterAsText(1)
useISO = "true"#arcpy.GetParameterAsText(2)
#r'E:\gpw\sen.gdb\sen_admin2_boundaries_2010_water_mask_clipped_intersect_projected'
joinField = "INTRSCTID"
featureArea = "AREAKM"
waterArea = "WATERAREAKM"
joinVariables = [waterArea]
fieldListWildCard = "*E_A*"
##workspace = r'E:\gpw\sen.gdb'

# parse inFC to determine rootName
if not useISO == "true":
    rNameParse = os.path.basename(clipnetInt).split("_")
    rootName = rNameParse[0] + "_" + rNameParse[1]
else:
   rootName = os.path.basename(clipnetInt)[:3]
# define input fishnet
inFish = rootName + "_fishnet"
# define estimatesTable
estimatesTable = rootName + "_estimates"
# define workspace environment
##arcpy.env.workspace = workspace

# Make Feature Layers
layer1 = os.path.basename(clipnetInt) + "_lyr"
layer2 = os.path.basename(joinFeature) + "_lyr"
try:
    addTime = datetime.datetime.now()
    if not arcpy.Exists(layer1):
        try:
            arcpy.MakeFeatureLayer_management(clipnetInt,layer1)
        except:
            arcpy.MakeTableView_management(clipnetInt,layer1)
    if not arcpy.Exists(layer2):
        try:
            arcpy.MakeFeatureLayer_management(joinFeature,layer2)
        except:
            arcpy.MakeTableView_management(joinFeature,layer2)
    print "Made Feature Layers"
    arcpy.AddMessage("Made Feature Layers")
    print datetime.datetime.now() - addTime
    arcpy.AddMessage(datetime.datetime.now() - addTime)
except:
    arcpy.GetMessages()
# Add Join
try:
    addTime = datetime.datetime.now()
    arcpy.AddJoin_management(layer1,joinField,layer2,joinField,"KEEP_COMMON")
    print "Added Join"
    arcpy.AddMessage("Added Join")
    print datetime.datetime.now() - addTime
    arcpy.AddMessage(datetime.datetime.now() - addTime)
except:
    print arcpy.GetMessages()
# Transfer areaField
##    # List Fields
##    fields = arcpy.ListFields(layer1,"*")
##    for field in fields:
##        print field.name
for joinVariable in joinVariables:
    print joinVariable
    try:
        addTime = datetime.datetime.now()
        expression = '!' + os.path.basename(joinFeature) + "." + joinVariable + '!'
        arcpy.CalculateField_management(layer1,os.path.basename(clipnetInt) + "." + joinVariable,expression,'PYTHON')
        print "Calculated " + joinVariable
        arcpy.AddMessage("Calculated " + joinVariable)
        print datetime.datetime.now() - addTime
        arcpy.AddMessage(datetime.datetime.now() - addTime)
    except:
        print arcpy.GetMessages()
try:
    addTime = datetime.datetime.now()
    arcpy.RemoveJoin_management(layer1,os.path.basename(joinFeature))
    print "Removed temporary join"
    arcpy.Delete_management(layer1)
    arcpy.Delete_management(layer2)
    arcpy.AddMessage("Removed temporary join")
    print datetime.datetime.now() - addTime
    arcpy.AddMessage(datetime.datetime.now() - addTime)
except:
    print arcpy.GetMessages()

# Need to convert Nulls to Zeros
try:
    waterLYR = "fishnetwaterlyr"
    arcpy.MakeFeatureLayer_management(clipnetInt,waterLYR,waterArea + " IS NULL")
    arcpy.CalculateField_management(waterLYR,waterArea,0, "PYTHON")
    print "Recoded Nulls"
except:
    arcpy.GetMessages()
    
