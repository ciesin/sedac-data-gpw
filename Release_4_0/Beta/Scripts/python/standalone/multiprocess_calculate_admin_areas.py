# original code adapted from grid-preprocess.py
# multiprocess_calculate_admin_areas
# calculate the administrative areas
# Kytt MacManus
# 8-28-15

# import libraries
import arcpy, os, sys, multiprocessing
import datetime

# helper method to join fields
def joinVariables(baseFeature,joinField,joinFeature,joinVariables):
    # Make Feature Layers
    layer1 = os.path.basename(baseFeature) + "_lyr"
    layer2 = os.path.basename(joinFeature) + "_lyr"
    try:
        addTime = datetime.datetime.now()
        if not arcpy.Exists(layer1):
            try:
                arcpy.MakeFeatureLayer_management(baseFeature,layer1)
            except:
                arcpy.MakeTableView_management(baseFeature,layer1)
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
        arcpy.AddJoin_management(layer1,joinField,layer2,joinField,"KEEP_ALL")
        print "Added Join"
        arcpy.AddMessage("Added Join")
        print datetime.datetime.now() - addTime
        arcpy.AddMessage(datetime.datetime.now() - addTime)
    except:
        print arcpy.GetMessages()
    for joinVariable in joinVariables:
        print joinVariable
        try:
            addTime = datetime.datetime.now()
            expression = '!' + os.path.basename(joinFeature) + "." + joinVariable + '!'
            arcpy.CalculateField_management(layer1,os.path.basename(baseFeature) + "." + joinVariable,expression,'PYTHON')
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


def calculateAdminAreas(gdb):
    startTime = datetime.datetime.now()
    #these variables must all be parsed from input gdb        
    # define inputs
    gdbName = os.path.basename(gdb)
    rootName = os.path.basename(gdb).replace(".gdb","")
    # grab inFC
    boundaryWS = r'G:\gpw\boundaries_hi_res.gdb'
    arcpy.env.workspace = boundaryWS                                    
    inFC = boundaryWS + os.sep + str(arcpy.ListFeatureClasses(rootName + "*")[0])
    print inFC
    workspace = gdb
    # define spatial reference
    prjFile = r'G:\gpw\custom_projections' + os.path.sep + rootName + "_fishnet_mollweide.prj"
    # check to see that estimates exists, if it doesn't kill the script
    if not arcpy.Exists(prjFile):
        arcpy.AddMessage("The input prj file does not exist, check the network")
        text="gpw"
        return text
    else:
        spatialRef = open(prjFile,"r").read()
        print prjFile
    # define gridding resolution
    # Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
    # 1 degree divided into 120 parts is 30 seconds
    linespd = 120
    # copy of inFC
    inFCG = gdb + os.sep + rootName + "_gridding"
    # tmpid field
    tmpid = "TEMPID"
    # mollweide version of fc
    projectFC = inFCG + "_mollweide"
    # calculated adminArea 
    adminArea = "ADMINAREAKM"
    maskedArea = "ADMINAREAKMMASKED"

    # need to replace with clipping water mask
    # if it has fatures then waterExist = True
    
    waterMask = rootName + "_water_mask"

    # define input waterMask
    waterTemplate = r'G:\gpw\water\water_inputs.gdb\water_mask_final'
    waterFC = gdb + os.sep + rootName + "_fishnet_water_areas"
    waterProjectFC = waterFC + "_mollweide"
    adminWaterArea = "ADMINWATERAREAKM"
    

    # define workspace environment
    arcpy.env.workspace = workspace
    if not arcpy.Exists(inFCG):
        # make a copy of inFC
        try:
            arcpy.Copy_management(inFC,inFCG)
            print "Created " + inFCG
        except:
            print arcpy.GetMessages()
            
        # add a tmpid field and calculate it equal to the OBJECTID
        try:
            arcpy.AddField_management(inFCG,tmpid,'TEXT')
            arcpy.CalculateField_management(inFCG,tmpid,'!UBID!','PYTHON')
            #print "calculated " + tmpid
        except:
            print arcpy.GetMessages()    

        # project inFCG to mollweide
        try:
            arcpy.Project_management(inFCG, projectFC, spatialRef)
            #print "created " + projectFC
        except:
            print arcpy.GetMessages()

        # add ADMINAREAKM and calculate
        try:
            arcpy.AddField_management(projectFC,adminArea,'DOUBLE')
            arcpy.AddField_management(inFCG,adminArea,'DOUBLE')
            arcpy.CalculateField_management(projectFC,adminArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
            arcpy.AddMessage("calculated " + adminArea)
        except:
            print arcpy.GetMessages()

        # join ADMINAREAKM to inFCG
        try:
            joinTime = datetime.datetime.now()
            joinVariables(inFCG,tmpid,projectFC,[adminArea])
    ##        arcpy.JoinField_management(inFCG,tmpid,projectFC,tmpid,adminArea)
            arcpy.AddMessage("joined " + adminArea + " to " + inFCG)
            arcpy.AddMessage(datetime.datetime.now() - joinTime)
            arcpy.Delete_management(projectFC)
        except:
            print arcpy.GetMessages()
        try:
            arcpy.Clip_analysis(inFCG,waterTemplate,waterFC)
            count = arcpy.GetCount_management(waterFC)
            if int(str(count))==0:
                waterExist = False
                arcpy.Delete_management(waterFC)
                #print "Deleted " + waterFC + " because it has no features"
            else:
                waterExist = True
        except:
            print arcpy.GetMessages()
            sys.exit()
        if waterExist == True:
            # project waterFC to mollweide
            try:
                arcpy.Project_management(waterFC, waterProjectFC, spatialRef)
                arcpy.AddMessage("created " + waterProjectFC)
            except:
                print arcpy.GetMessages()
            # add ADMINWATERAREAKM and calculate
            try:
                arcpy.AddField_management(waterProjectFC,adminWaterArea,'DOUBLE')
                arcpy.AddField_management(inFCG,adminWaterArea,'DOUBLE')
                arcpy.CalculateField_management(waterProjectFC,adminWaterArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
                arcpy.AddMessage("calculated " + adminWaterArea)
            except:
                print arcpy.GetMessages()

            # join ADMINWATERAREAKM to inFCG
            try:
                joinTime = datetime.datetime.now()
                joinVariables(inFCG,tmpid,waterProjectFC,[adminWaterArea])
    ##            arcpy.JoinField_management(inFCG,tmpid,waterProjectFC,tmpid,adminWaterArea)
                arcpy.AddMessage("joined " + adminWaterArea + " to " + inFCG)
                arcpy.AddMessage(datetime.datetime.now() - joinTime)
                arcpy.Delete_management(waterProjectFC)
            except:
                print arcpy.GetMessages()

            # Need to convert Nulls to Zeros
            try:
                adminWaterLYR = os.path.basename(inFCG) + "_adminwaterlyr"
                arcpy.MakeFeatureLayer_management(inFCG,adminWaterLYR,adminWaterArea + " IS NULL")
                arcpy.CalculateField_management(adminWaterLYR,adminWaterArea,0, "PYTHON")
                arcpy.AddMessage("Recoded Nulls")
                
            except:
                print arcpy.GetMessages()
        else:
            # add ADMINWATERAREAKM and calculate
            try:
                adminWaterArea = "ADMINWATERAREAKM"
                arcpy.AddField_management(inFCG,adminWaterArea,'DOUBLE')
                arcpy.CalculateField_management(inFCG,adminWaterArea,0,'PYTHON')
                arcpy.AddMessage("calculated " + adminWaterArea)
            except:
                print arcpy.GetMessages()

        ## add ADMINAREAKMMASKED to inFCG and calculate
        try:
            arcpy.AddField_management(inFCG,maskedArea,'DOUBLE')
            arcpy.CalculateField_management(inFCG,maskedArea,'!' + adminArea + '! - !' + adminWaterArea + "!",'PYTHON')
            arcpy.AddMessage("calculated " + maskedArea)
        except:
            print arcpy.GetMessages()
            
        # Need to convert Negatives to Zeros
        try:
            adminMaskedLYR = os.path.basename(inFCG) + "_adminmaskedlyr"
            arcpy.MakeFeatureLayer_management(inFCG,adminMaskedLYR,maskedArea + " < 0")
            if int(arcpy.GetCount_management(adminMaskedLYR)[0])>0:
                arcpy.CalculateField_management(adminMaskedLYR,maskedArea,0, "PYTHON")
            arcpy.AddMessage("Recoded Negatives")
        except:
            print arcpy.GetMessages()
        text = "processed " + gdb
        return text

def main():
    # The number of jobs is equal to the number of shapefiles
    workspace = r'E:\gpw\v4processing\inputs'
    usaSpace = r'E:\gpw\v4processing\inputs\usa\tiles'
    workspaces = [workspace]#,usaSpace]
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
        gdbs.sort()
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt)    
       
    print "processing"
    for gdb in gdb_list:
        print gdb
        print calculateAdminAreas(gdb)

if __name__ == '__main__':
    main()
