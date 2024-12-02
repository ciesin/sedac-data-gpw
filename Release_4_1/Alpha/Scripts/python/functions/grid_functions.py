# import libraries
import arcpy, sys, os, datetime

# define set of worker functions which are usable by process functions
def joinVariables(baseFeature,joinField,joinFeature,joinFields,joinType):
    '''Helper method to join fields'''
    # Make Feature Layers
    layer1 = os.path.basename(baseFeature) + "_lyr"
    layer2 = os.path.basename(joinFeature) + "_lyr"
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
    # Add Join
    arcpy.AddJoin_management(layer1,joinField,layer2,joinField,joinType)
    # calculate join variables
    for joinVariable in joinFields:
        expression = '!' + os.path.basename(joinFeature) + "." + joinVariable + '!'
        arcpy.CalculateField_management(layer1,os.path.basename(baseFeature) + "." + joinVariable,expression,'PYTHON')
    # clean up
    arcpy.RemoveJoin_management(layer1,os.path.basename(joinFeature))
    arcpy.Delete_management(layer1)
    arcpy.Delete_management(layer2)
    

# define process functions
def calculateEstimates(gdb):
    startTime = datetime.datetime.now()
    '''Calculate Estimates for Range of Target Years based on AGR'''
    try:
        iso = os.path.basename(gdb)[:-4].upper()
        # get agrFile
        agrWS = r'\\Dataserver0\gpw\GPW4\Beta\GrowthRate\country_tables_beta.gdb'
        arcpy.env.workspace = agrWS
        agrFile = agrWS + os.sep + arcpy.ListTables(iso + "*")[0]
        # create search cursor in order to determine agrid_source
        searchCursor = arcpy.SearchCursor(agrFile)
        searchCount = 0
        searchRow = searchCursor.next()
        while searchCount == 0:
            agrid_source = searchRow.getValue('agrid_source')
            searchCount = 1
        del searchRow
        del searchCursor
        # parse agrid
        agridSplit = agrid_source.split('_')
        # parse agrid expression
        if len(agridSplit)==1:
            agridExp = '!' + agridSplit[0] + '!'
        else:
            agridFields = iter(agridSplit)
            next(agridFields)
            agridExp = '!' + agridSplit[0] + '!'
            for expField in agridFields:
                agridExp = agridExp + ' + ' + '"' + '_' + '" ' + '+ ' + '!' + expField + '!'
        
        # get popFile
        arcpy.env.workspace = gdb
        popFile = gdb + os.sep + str(arcpy.ListTables("*pop_input")[0])
        # create estimatesTable
        estimatesTable = popFile.replace("_input","_estimates")
        arcpy.CopyRows_management(popFile,estimatesTable)
        # add and calculate agrid
        arcpy.AddField_management(estimatesTable,"AGRID","TEXT","","",200)
        arcpy.CalculateField_management(estimatesTable, "AGRID", agridExp,"PYTHON")

        # copy agrFile to agrTable
        agrTable = gdb + os.sep + os.path.basename(agrFile.lower())
        arcpy.CopyRows_management(agrFile,agrTable)
        # create search cursor in order to determine rpopyear
        searchCursor = arcpy.SearchCursor(estimatesTable)
        searchCount = 0
        searchRow = searchCursor.next()
        while searchCount == 0:
            rpopyear = searchRow.getValue('RPOPYEAR')
            searchCount = 1
        del searchRow
        del searchCursor
        # join agr fields
        joinField = "AGRID"
        arcpy.JoinField_management(estimatesTable,joinField,agrTable,"agrid",["agr","gr_start_year","gr_end_year"])
        # define target years
        targetYears = ["1975","1990","2000","2005","2010","2015","2020"]
        # iterate
        for year in targetYears:
            # determine AGR exp by year - rpopyear
            yearTo = str(int(year) - int(rpopyear))
            eField = "E_ATOTPOPBT_" + year
            arcpy.AddField_management(estimatesTable,eField,"LONG")
            calcExpression = "!ATOTPOPBT! * math.exp( !agr! * " + yearTo + " )"
            arcpy.CalculateField_management(estimatesTable,eField,calcExpression,"PYTHON_9.3")
        # finally summarize the atotpopbt and the estimates fields national
        summaryFields = [["RPOPYEAR","FIRST"],["gr_start_year","FIRST"],
                         ["gr_end_year","FIRST"],["ISO","FIRST"],
                         ["ATOTPOPBT","SUM"],["E_ATOTPOPBT_1975","SUM"],
                         ["E_ATOTPOPBT_1990","SUM"],["E_ATOTPOPBT_2000","SUM"],
                         ["E_ATOTPOPBT_2005","SUM"],["E_ATOTPOPBT_2010","SUM"],
                         ["E_ATOTPOPBT_2015","SUM"],["E_ATOTPOPBT_2020","SUM"]]                
        summaryTable = estimatesTable + "_summary"
        arcpy.Statistics_analysis(estimatesTable,summaryTable,summaryFields)
        return "Calculated target year estimates for " + iso + ": " + str(datetime.datetime.now()-startTime) 
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    
def calculateSexProportions(gdb):
    startTime = datetime.datetime.now()
    '''Create Sex Proprtions Table'''
    arcpy.env.workspace = gdb
    if os.path.basename(gdb)=="vcs.gdb":
        pass
    
    try:
        iso = os.path.basename(gdb)[:-4].upper()
        # define files to work with
        popFile = arcpy.ListTables("*pop_input")[0]
        sexFile = arcpy.ListTables("*sex_variables_input")[0]
        sexProportions = gdb + os.sep + sexFile.replace("_input","_proportions")
        # create output table
        arcpy.CopyRows_management(sexFile,sexProportions)

        # add and calculate CALC_ATOTPOPBT as ATOTPOPFT + ATOTPOPMT
        # to ensure that the denominator results in proportions that
        # sum to 1
        arcpy.AddField_management(sexProportions,"CALC_ATOTPOPBT","LONG")
        arcpy.CalculateField_management(sexProportions,"CALC_ATOTPOPBT","!ATOTPOPMT!+!ATOTPOPFT!","PYTHON")

        # create table view to avoid division by 0
        vTable = os.path.basename(sexProportions) + "_VIEW"
        vExpression = '"CALC_ATOTPOPBT" > 0'
        arcpy.MakeTableView_management(sexProportions, vTable, vExpression)  
        # add prop fields and calculate
        mProp = "ATOTPOPMTPROP"
        arcpy.AddField_management(vTable,mProp,"DOUBLE")
        mCalc = "float(!ATOTPOPMT!)/float(!CALC_ATOTPOPBT!)"
        arcpy.CalculateField_management(vTable,mProp,mCalc,"PYTHON")
        fProp = "ATOTPOPFTPROP"
        arcpy.AddField_management(vTable,fProp,"DOUBLE")
        fCalc = "float(!ATOTPOPFT!)/float(!CALC_ATOTPOPBT!)"
        arcpy.CalculateField_management(vTable,fProp,fCalc,"PYTHON")
        # create table view to fill in nulls
        # define view
        view0 = os.path.basename(sexProportions) + "_NULL"
        # define calculation expression
        expression0 = '"CALC_ATOTPOPBT" = 0' 
        arcpy.MakeTableView_management(sexProportions, view0, expression0)
        arcpy.CalculateField_management(view0, mProp, "0", "PYTHON")
        arcpy.CalculateField_management(view0, fProp, "0", "PYTHON")
        # success
        return "Calculated sex proportions for " + iso + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso + " error: " + str(arcpy.GetMessages())

def joinSexData(gdb):
    startTime = datetime.datetime.now()
    '''Join Sex Variables to Estimates Table and Calculate 2010 Estimates'''
    arcpy.env.workspace = gdb
    if os.path.basename(gdb)=="vcs.gdb":
        pass
    try:
        iso = os.path.basename(gdb)[:-4].upper()
        # define files to work with
        popFile = arcpy.ListTables("*pop_input")[0]
        sexProportions = arcpy.ListTables("*sex_variables_proportions")[0]
        estimatesTable = str(popFile).replace("_input","_estimates")
        # add and calculate VARID, and SPOPYEAR and SPOPLEVEL
        arcpy.AddField_management(estimatesTable,"VARID","TEXT","","",200)
        arcpy.AddField_management(estimatesTable,"SPOPYEAR","SHORT")
        arcpy.AddField_management(estimatesTable,"SPOPLEVEL","SHORT")
        # parse VARID_SOURCE to create expression and grab year
        with arcpy.da.SearchCursor(sexProportions,["VARID_SOURCE","RPOPYEAR"]) as rows:
            for row in rows:
                VARIDSOURCE = str(row[0])
                SPOPYEAR = int(row[1])
                break
        for varItem in VARIDSOURCE.split("_"):
                if varItem == VARIDSOURCE.split("_")[0]:
                    expression = "!" + varItem + "!"
                else:
                    expression = expression + '+"_"+' + "!" + varItem + "!"
        SPOPLEVEL = len(VARIDSOURCE.split("_"))-1
        # perform calculations
        arcpy.CalculateField_management(estimatesTable,"SPOPYEAR",SPOPYEAR,"PYTHON")
        arcpy.CalculateField_management(estimatesTable,"SPOPLEVEL",SPOPLEVEL,"PYTHON")
        arcpy.CalculateField_management(estimatesTable,"VARID",expression,"PYTHON")
        # try to add ATOTPOPMT and ATOTPOPFT
        arcpy.AddField_management(estimatesTable,"E_ATOTPOPMT_2010","LONG")
        arcpy.AddField_management(estimatesTable,"E_ATOTPOPFT_2010","LONG")
        # define fields to join
        mProp = "ATOTPOPMTPROP"
        fProp = "ATOTPOPFTPROP"
        joinFields = [mProp,fProp]
        arcpy.AddField_management(estimatesTable,mProp,"DOUBLE")
        arcpy.AddField_management(estimatesTable,fProp,"DOUBLE")
        # execute join
        joinVariables(estimatesTable,"VARID",sexProportions,joinFields,"KEEP_COMMON")
        # apply proportions to E_ATOTPOPBT_2010
        for joinVariable in joinFields:
            if joinVariable == mProp:
                sField = "E_ATOTPOPMT_2010"
            elif joinVariable == fProp:
                sField = "E_ATOTPOPFT_2010"
            # perform calculation
            expression = '!' + joinVariable + '!*!E_ATOTPOPBT_2010!'
            arcpy.CalculateField_management(estimatesTable,sField,expression,'PYTHON')
            # clean up
            arcpy.DeleteField_management(estimatesTable,joinVariable)
        # success
        return "Calculated sex estimates for 2010 for " + iso + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    
def calculateAdminAreas(gdb):
    startTime = datetime.datetime.now()
    '''Calculate Administrative Areas'''
    iso = os.path.basename(gdb)[:-4]
    rootName = os.path.basename(gdb).replace(".gdb","")
    gdb = gdb.replace(".gdb","_features.gdb")
    if not arcpy.Exists(gdb):
        arcpy.CreateFileGDB_management(os.path.dirname(gdb),os.path.basename(gdb)[:-4])
    try:
        # define files to work with
        gdbName = os.path.basename(gdb)
        waterTemplate = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\ancillary.gdb\water_mask_final'
        # grab inFC
        boundaryWS = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\features\from_sde\country_boundaries_hi_res.gdb'
        arcpy.env.workspace = boundaryWS                                    
        inFC = boundaryWS + os.sep + str(arcpy.ListFeatureClasses(iso + "*")[0])
        # define spatial reference
        prjFile = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\custom_projections' + os.path.sep + iso + "_fishnet_mollweide.prj"
        # check to see that estimates exists, if it doesn't kill the script
        if not arcpy.Exists(prjFile):
            return "Cannot complete operation because PRJ file is missing: " + prjFile
        spatialRef = open(prjFile,"r").read()
        # copy inFC
        arcpy.env.workspace = gdb
        inFCG = gdb + os.sep + os.path.basename(inFC)
        arcpy.Copy_management(inFC,inFCG)
        # add a tmpid field and calculate it equal to the OBJECTID
        tmpid = "TEMPID"
        adminArea = "ADMINAREAKM"
        adminWaterArea = "ADMINWATERAREAKM"
        maskedArea = "ADMINAREAKMMASKED"
        arcpy.AddField_management(inFCG,tmpid,'LONG')
        arcpy.CalculateField_management(inFCG,tmpid,'!OBJECTID!','PYTHON')
        arcpy.AddField_management(inFCG,adminArea,'DOUBLE')
        arcpy.AddField_management(inFCG,adminWaterArea,'DOUBLE')
        arcpy.AddField_management(inFCG,maskedArea,'DOUBLE')
        # project inFCG to mollweide
        projectFC = inFCG + "_mollweide"
        arcpy.Project_management(inFCG, projectFC, spatialRef)
        # calculate adminArea 
        arcpy.CalculateField_management(projectFC,adminArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
        # join ADMINAREAKM to inFCG
        joinVariables(inFCG,tmpid,projectFC,[adminArea],"KEEP_ALL")
        # evaluate for existence of water features
        waterFC = gdb + os.sep + rootName + "_water_areas"
        arcpy.Clip_analysis(inFCG,waterTemplate,waterFC)
        count = arcpy.GetCount_management(waterFC)
        if int(str(count))==0:
            waterExist = False
            arcpy.Delete_management(waterFC)
        else:
            waterExist = True
        if waterExist == True:
            # project waterFC to mollweide
            waterProjectFC = waterFC + "_mollweide"
            arcpy.Project_management(waterFC, waterProjectFC, spatialRef)
            # calculate ADMINWATERAREAKM
            arcpy.CalculateField_management(waterProjectFC,adminWaterArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
            # join ADMINWATERAREAKM to inFCG
            joinVariables(inFCG,tmpid,waterProjectFC,[adminWaterArea],"KEEP_ALL")
            # convert Nulls to Zeros
            adminWaterLYR = os.path.basename(inFCG) + "_adminwaterlyr"
            arcpy.MakeFeatureLayer_management(inFCG,adminWaterLYR,adminWaterArea + " IS NULL")
            arcpy.CalculateField_management(adminWaterLYR,adminWaterArea,0, "PYTHON")
        else:
            # calculate ADMINWATERAREAKM
            arcpy.CalculateField_management(inFCG,adminWaterArea,0,'PYTHON')
        # calculate ADMINAREAKMMASKED
        arcpy.CalculateField_management(inFCG,maskedArea,'!' + adminArea + '! - !' + adminWaterArea + "!",'PYTHON')
        # convert Negatives to Zeros
        adminMaskedLYR = os.path.basename(inFCG) + "_adminmaskedlyr"
        arcpy.MakeFeatureLayer_management(inFCG,adminMaskedLYR,maskedArea + " < 0")
        if int(arcpy.GetCount_management(adminMaskedLYR)[0])>0:
            arcpy.CalculateField_management(adminMaskedLYR,maskedArea,0, "PYTHON")          
        # success
        return "Calculated administrative areas for " + iso.upper() + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso.upper() + " error: " + str(arcpy.GetMessages())

def joinEstimatesCalculateDensities(gdb):
    startTime = datetime.datetime.now()
    '''joinEstimatesCalculateDensities'''
    iso = os.path.basename(gdb)[:-4]
    rootName = iso
    tblSel = rootName + '_tblSel'
    arcpy.env.workspace = gdb
    try:
        # grab estimates table
        estimatesTable = gdb + os.sep + arcpy.ListTables("*_estimates")[0]
        # grab matching boundary
        boundaryWorkspace = gdb.replace(".gdb","_features.gdb")
        arcpy.env.workspace = boundaryWorkspace
        boundaryFC = arcpy.ListFeatureClasses(iso + "*")[0]
        if len(arcpy.ListFields(boundaryFC,"E_ATOTPOPBT_2010"))==0:
            # join the estimates table
            arcpy.JoinField_management(boundaryFC,"UBID",estimatesTable,"UBID")
            arcpy.DeleteField_management(boundaryFC,["UBID_1","AGRID","VARID"])
            # Isolate boundaries with null estimates for review
            cntLyr = iso+"lyr"
            outCnt = boundaryFC + "_unjoined"
            if int(arcpy.GetCount_management(
                arcpy.MakeFeatureLayer_management(boundaryFC,cntLyr,
                                                  """"E_ATOTPOPBT_2010" IS NULL AND "BOUNDARY_CONTEXT" IS NULL AND "POP_CONTEXT" IS NULL"""))[0])>0:
                arcpy.CopyFeatures_management(cntLyr,outCnt)
                return iso.upper() + " error: some unjoined units to check"
            
        # define list of fields to calculate densities
        fieldList = ["E_ATOTPOPBT_1975","E_ATOTPOPBT_1990","E_ATOTPOPBT_2000",
                     "E_ATOTPOPBT_2005","E_ATOTPOPBT_2010","E_ATOTPOPBT_2015",
                     "E_ATOTPOPBT_2020","E_ATOTPOPFT_2010","E_ATOTPOPMT_2010"]
        # Create a table view to avoid division by zero
        whereCls = """"ADMINAREAKMMASKED" > 0"""
        tblSel = arcpy.MakeTableView_management(boundaryFC,tblSel,whereCls)
        for field in fieldList:
            # define density field
            dsField = field + "_DS"
            # define masked density field
            maskedDSField = field + "_DSM"
            # add density field and masked density field
            arcpy.AddField_management(boundaryFC,dsField,'DOUBLE')
            arcpy.AddField_management(boundaryFC,maskedDSField,'DOUBLE')
            # do the division
            exp = 'float(!' + field + '!) / float(!ADMINAREAKM!)'
            exp2 = 'float(!' + field + '!) / float(!ADMINAREAKMMASKED!)'
            arcpy.CalculateField_management(tblSel,dsField,exp,'PYTHON')
            arcpy.CalculateField_management(tblSel,maskedDSField,exp2,'PYTHON')
        # success
        return "Joined attributes and calculated densities for: " + iso.upper() + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso.upper() + " error: " + str(arcpy.GetMessages())

def intersect(gdb):
    startTime = datetime.datetime.now()
    '''Intersect Features and Fishnet'''
    iso = os.path.basename(gdb)[:-4]
    rootName = iso
    try:
        # define inputs
        fishGDB = gdb.replace(".gdb","_fishnet.gdb")
        fishnet = fishGDB + os.sep + rootName + "_fishnet"
        boundaryWS = gdb.replace(".gdb","_features.gdb")
        arcpy.env.workspace = boundaryWS
        inFC = boundaryWS + os.sep + str(arcpy.ListFeatureClasses(rootName + "*2010")[0])
        waterMaskProj = boundaryWS + os.sep + rootName + "_water_areas_mollweide"
        clipwatInt = fishGDB + os.sep + rootName + "_water_mask_clipped_intersect"
        clipwatProj = clipwatInt + "_mollweide"
        # define spatial reference
        prjFile = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\custom_projections' + os.path.sep + iso + "_fishnet_mollweide.prj"
        # check to see that estimates exists, if it doesn't kill the script
        if not arcpy.Exists(prjFile):
            return "Cannot complete operation because PRJ file is missing: " + prjFile
        spatialRef = open(prjFile,"r").read()
        # intersect fishnet and inFCG
        clipnetInt = fishnet + "_intersect"
        clipnetProj = clipnetInt + "_mollweide"
        fishnetClip = "in_memory" + os.sep + rootName + "clipped"
        arcpy.Clip_analysis(fishnet,inFC,fishnetClip)
        inFeatures = [inFC,fishnetClip]
        arcpy.Intersect_analysis(inFeatures, clipnetInt)
        # add area fields
        arcpy.AddField_management(clipnetInt,"AREAKM",'DOUBLE')
        arcpy.AddField_management(clipnetInt,"WATERAREAKM",'DOUBLE')
        arcpy.AddField_management(clipnetInt,"AREAKMMASKED",'DOUBLE')
        # add intersectid and index it
        arcpy.AddField_management(clipnetInt,"INTERSECTID","LONG")
        arcpy.CalculateField_management(clipnetInt,"INTERSECTID",
                                        "!OBJECTID!","PYTHON")
        arcpy.AddIndex_management(clipnetInt,"INTERSECTID",
                               "INTERSECTID_INDEX","UNIQUE","ASCENDING")
        # project to custom mollweide to calculate areas
        arcpy.Project_management(clipnetInt, clipnetProj, spatialRef)
        arcpy.AddField_management(clipnetProj,"AREAKM",'DOUBLE')
        arcpy.CalculateField_management(clipnetProj,"AREAKM",
                                        '!shape.area@SQUAREKILOMETERS!'
                                        ,'PYTHON')
        # if waterMaskProj does not exist then complete calculations
        if not arcpy.Exists(waterMaskProj):
            arcpy.CalculateField_management(clipnetProj,"WATERAREAKM",0, "PYTHON")
            arcpy.CalculateField_management(clipnetProj,"AREAKMMASKED","!AREAKM!","PYTHON")
        # otherwise calculate the intersected water areas
        else:
            arcpy.Clip_analysis(clipnetProj,waterMaskProj,clipwatProj)
            arcpy.CalculateField_management(clipwatProj,"WATERAREAKM",
                                            '!shape.area@SQUAREKILOMETERS!'
                                            ,'PYTHON')
            # join variables
            joinVariables(clipnetProj,"INTERSECTID",clipwatProj,["WATERAREAKM"],"KEEP_COMMON")
            # create views to fill in missing waterareakm and to control for noise in areakmmasked
            waterLYR = rootName + "_fishnetwaterlyr"
            arcpy.MakeFeatureLayer_management(clipnetProj,waterLYR,
                                              '"'+"WATERAREAKM"+'"'+" IS NULL")
            arcpy.CalculateField_management(waterLYR,"WATERAREAKM",0, "PYTHON")
            arcpy.CalculateField_management(clipnetProj,"AREAKMMASKED",
                                            '!AREAKM! - !WATERAREAKM!',
                                            'PYTHON')
            maskedLYR = rootName + "_maskedlyr"
            arcpy.MakeFeatureLayer_management(clipnetProj,maskedLYR,'"'+"AREAKMMASKED"+'"'+" < 0.0000001")
            arcpy.CalculateField_management(maskedLYR,"AREAKMMASKED",0, "PYTHON")
        # success
        return "Intesected fishnet and calculated pixel areas: " + iso.upper() + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso.upper() + " error: " + str(arcpy.GetMessages())
        
def calculateIntersectCounts(gdb):
    startTime = datetime.datetime.now()
    '''Calculate Intersect Counts and Join to Fishnet'''
    iso = os.path.basename(gdb)[:-4]
    rootName = os.path.basename(gdb).replace(".gdb","")
    try:
        # define inputs
        fishGDB = gdb.replace(".gdb","_fishnet.gdb")
        fishnet = fishGDB + os.sep + rootName + "_fishnet"
        clipnetInt = fishnet + "_intersect"
        clipnetProj = clipnetInt + "_mollweide"
        sumTable = fishGDB + os.sep + rootName + "_count_summary"
        # create list of sumFields for calculating statistics
        sumFields = [['AREAKM','SUM'],['WATERAREAKM','SUM'],['AREAKMMASKED','SUM']]
        # list dsm fields and calculate cntm
        dsmFields = arcpy.ListFields(clipnetProj,"*DSM")
        for dsmField in dsmFields:
            cntField = str(dsmField.name).replace("DSM","CNTM")
            # add to sumFields
            sumFields.append([cntField,'SUM'])
            # add cntField to fishnet
            arcpy.AddField_management(clipnetProj,cntField,"DOUBLE")
            arcpy.CalculateField_management(clipnetProj,cntField,
                                            "!AREAKMMASKED!*!"+dsmField.name+"!","PYTHON")
        # calculate statistics and add index
        arcpy.Statistics_analysis(clipnetProj,sumTable,sumFields,"PIXELID")
        arcpy.AddIndex_management(sumTable,"PIXELID","PIXELID_index","UNIQUE")
        # list fields to join from sumTable
        cntFields = arcpy.ListFields(sumTable,"SUM*")
        joinFields = ['PIXELID']
        targFields = ['PIXELID']
        # add fields to fishnet
        for cntField in cntFields:
            joinFields.append(cntField.name)
            newName = str(cntField.name).replace("SUM_","")
            targFields.append(newName)
            arcpy.AddField_management(fishnet,newName,"DOUBLE")
        # create dictionary of table values     
        joinDict = {}
        with arcpy.da.SearchCursor(sumTable, joinFields) as rows:
            for row in rows:
                joinval = row[0]
                val1 = row[1]
                val2 = row[2]
                val3 = row[3]
                val4 = row[4]
                val5 = row[5]
                val6 = row[6]
                val7 = row[7]
                val8 = row[8]
                val9 = row[9]
                val10 = row[10]
                val11 = row[11]
                val12 = row[12]
                joinDict[joinval]=[val1,val2,val3,
                                   val4,val5,val6,
                                   val7,val8,val9,
                                   val10,val11,val12]
        del row, rows
        # create update cursor
        with arcpy.da.UpdateCursor(fishnet, targFields) as recs:
            for rec in recs:
                keyval = rec[0]
                if joinDict.has_key(keyval):
                    rec[1] = joinDict[keyval][0]
                    rec[2] = joinDict[keyval][1]
                    rec[3] = joinDict[keyval][2]
                    rec[4] = joinDict[keyval][3]
                    rec[5] = joinDict[keyval][4]
                    rec[6] = joinDict[keyval][5]
                    rec[7] = joinDict[keyval][6]
                    rec[8] = joinDict[keyval][7]
                    rec[9] = joinDict[keyval][8]
                    rec[10] = joinDict[keyval][9]
                    rec[11] = joinDict[keyval][10]
                    rec[12] = joinDict[keyval][11]
                else:
                    rec[1] = None
                    rec[2] = None
                    rec[3] = None
                    rec[4] = None
                    rec[5] = None
                    rec[6] = None
                    rec[7] = None
                    rec[8] = None
                    rec[9] = None
                    rec[10] = None
                    rec[11] = None
                    rec[12] = None
                recs.updateRow(rec)
        del rec, recs
        # success
        return "Calculated and joined masked counts for " + iso.upper() + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso.upper() + " error: " + str(arcpy.GetMessages())

def gridAndSummarize(gdb):
    '''grid variables and generate summary tables'''
    # set time counter
    startTime = datetime.datetime.now()
    # define paths
    gdbName = os.path.basename(gdb)
    iso = os.path.basename(gdb)[:-4].upper()
    rootName = os.path.basename(gdb).replace(".gdb","")
    try:
        arcpy.CheckOutExtension('SPATIAL')
        # define zone raster
        zoneRaster = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\ancillary\gpw4_extent.tif'
        # define schema table
        schemaTable = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb\count_raster_summary'
        # define inputs
        fishGDB = gdb.replace(".gdb","_fishnet.gdb")
        rasterDir = os.path.dirname(gdb) + os.sep + 'rasters'
        #os.path.dirname(gdb).replace("fishnets","rasters")
        outGDB = rasterDir + os.sep + rootName + ".gdb"
        # define inputs
        fishnet = fishGDB + os.sep + rootName + "_fishnet"
        # create gdb
        arcpy.CreateFileGDB_management(rasterDir,rootName)
        # Define Workspace
        arcpy.env.workspace = outGDB
        # Coordinate System
        wgs84 = arcpy.SpatialReference(4326)
        # Describe Fish
        desc = arcpy.Describe(fishnet)
        # Calculate Raster Extent
        extent = desc.Extent
        xmin = int(round(extent.XMin - .5))
        xmax = int(round(extent.XMax + .5))
        ymin = int(round(extent.YMin - .5))
        ymax = int(round(extent.YMax + .5))
        linespd = 120## Update As Needed
        cellSize = 1.0 / linespd
        # set raster envs
        arcpy.env.extent = arcpy.Extent(xmin,ymin,xmax,ymax)
        arcpy.env.outputCoordinateSystem = wgs84
        arcpy.env.cellSize = cellSize
        outAreaGrid = outGDB + os.sep + rootName.upper() + "_AREAKMMASKED"
        arcpy.PolygonToRaster_conversion(fishnet,"AREAKMMASKED",outAreaGrid,'CELL_CENTER','#',cellSize)
        outWaterAreaGrid = outGDB + os.sep + rootName.upper() + "_WATERAREAKM"
        arcpy.PolygonToRaster_conversion(fishnet,"WATERAREAKM",outWaterAreaGrid,'CELL_CENTER','#',cellSize)
        # list the E_ fields and grid them
        gridFields = arcpy.ListFields(fishnet,"E_*")
        for gridField in gridFields:
            fieldName = gridField.name
            outGrid = outGDB + os.sep + rootName.upper() + "_" + fieldName
            arcpy.PolygonToRaster_conversion(fishnet,fieldName,outGrid,'CELL_CENTER','#',cellSize)
        # set workspace
        arcpy.env.workspace = outGDB
        # list totpop rasters
        rasters = arcpy.ListRasters("*ATOTPOP*")
        # create a copy of the schema table
        summaryTable = outGDB + os.sep + iso + "_count_raster_summary"
        arcpy.CopyRows_management(schemaTable,summaryTable)
        # iterate the rasters
        i = 0
        for raster in rasters:
            year = raster.split("_")[3]
            # calculate a zonal statistics in memory
            zonalStat = "in_memory" + os.sep + iso + "_" + raster
            arcpy.sa.ZonalStatisticsAsTable(zoneRaster,"Value",raster,zonalStat,
                                            "DATA","SUM")
            # grab the pop value
            with arcpy.da.SearchCursor(zonalStat,"SUM") as rows:
                for row in rows:
                    popValue = row[0]
            # add the value to the summaryTable
            # if it is the first iteration insert,
            # otherwise update
            if i == 0:
                i = 1
                cursor = arcpy.InsertCursor(summaryTable)
                row = cursor.newRow()
                row.setValue("ISO",iso)
                row.setValue(raster[4:-5],popValue)
                cursor.insertRow(row)
                
                del cursor
                del row
            else:
                with arcpy.da.UpdateCursor(summaryTable,[raster[4:-5]]) as cursor:
                    for row in cursor:
                        row[0] = popValue
                        cursor.updateRow(row)
        # success
        return "Rasterized and summarized variables for " + iso.upper() + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso.upper() + " error: " + str(arcpy.GetMessages())


    
# define a main in order to test and troubleshoot functions
def main():
    scriptTime = datetime.datetime.now()
    gdb = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\ken.gdb'
##    print calculateEstimates(gdb)
##    print calculateSexProportions(gdb)
##    print joinSexData(gdb)
##    print calculateAdminAreas(gdb)
##    print joinEstimatesCalculateDensities(gdb)
##    print intersect(gdb)
##    print calculateIntersectCounts(gdb)
    print gridAndSummarize(gdb)
                                       
                                       
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
if __name__ == '__main__':
    main()
    

    
    
    
