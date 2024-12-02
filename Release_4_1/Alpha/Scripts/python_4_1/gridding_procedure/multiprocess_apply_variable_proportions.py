# apply variable proportions
# script generates proportions from age, sex, and age sex tables
import os, datetime
import multiprocessing
import arcpy
arcpy.env.overwriteOutput=True
scriptTime = datetime.datetime.now()
def applyProportions(estimatesIn,estimatesDict,searchFields,propDict,crossTabFlag):
    returnList=[]
    arcpy.env.overwriteOutput=True
    # read the estimates table into memory
    inMemEst = 'in_memory' + os.sep + os.path.basename(estimatesIn)
    arcpy.CopyRows_management(estimatesIn,inMemEst)
    # cycle the searchFields and add them to inMemEst
    uFields = ["USCID"]
    for sField in searchFields:
        uField = "E_"+sField+"_2010"
        if sField =="USCID":
            continue
        # check if it is already in the table
        if len(arcpy.ListFields(inMemEst,sField))>0:
            uFields.append(uField)
        else:
            arcpy.AddField_management(inMemEst, uField, "DOUBLE")
            uFields.append(uField)
    
    # finally perform the calculations
    try:
        with arcpy.da.UpdateCursor(inMemEst,uFields) as updateRows:
            for urow in updateRows:
                uscid = urow[0]
                if crossTabFlag==0:
                    try:
                        totalPop = estimatesDict[uscid][1]
                        if totalPop == None:
                            continue
                    except:
                        return (0,'could not get totalpop',estimatesDict, uscid)
                    rowIndex = 0
                    for value in urow:
                        if rowIndex == 0:
                            rowIndex+=1
                            continue
                        else:
                            try:
                                propRow = propDict[uscid]
                                propValue = propRow[rowIndex]                
                                urow[rowIndex] = totalPop * propValue
                                rowIndex+=1
                            except:
                                return(0,'could not get totalpop prop',uFields,urow,propRow,propValue)
##                                returnList.append(uFields,urow,propRow,propValue)
                    try:
                        updateRows.updateRow(urow)
                    except:
                        return (0,uFields,urow)
##                        returnList.append(uFields,urow)
                else:
                    try:
                        totalFPop = estimatesDict[uscid][2]
                        if totalFPop == None:
                            continue
                        totalMPop = estimatesDict[uscid][1]
                        if totalMPop == None:
                            continue
                    except:
                        return (0,'could not get M/F pop',uscid)
                    rowIndex = 0
                    for value in urow:
                        if rowIndex == 0:
                            rowIndex+=1
                            continue
                        else:
                            try:
                                propRow = propDict[uscid]
                                propValue = propRow[rowIndex]
                                if rowIndex % 2 == 0:
                                    urow[rowIndex] = totalFPop * propValue
                                else:
                                    urow[rowIndex] = totalMPop * propValue
                                rowIndex+=1
                            except:
                                return (0,'could not get M/F props',uFields,urow,propRow,propValue)
                    try:
                        updateRows.updateRow(urow)
    ##                    return (0, urow)
                    except:
                        returnList.append(uFields,urow)
        # copy the file back to disk and delete the in memory copy
        arcpy.CopyRows_management(inMemEst,estimatesIn)
        arcpy.Delete_management(inMemEst)
        return (1,estimatesIn)
    except:
        return (0,returnList,urow,arcpy.GetMessages())

    
                       
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
def calculateSexProportions(inSexTable):
    arcpy.env.overwriteOutput=True
    returnList = []
    sexProportions = inSexTable + "_proportions"
    try:
        arcpy.CopyRows_management(inSexTable,sexProportions)
        # add CALCATOTPOPBT PROPMT and PROPFT
        try:
            arcpy.AddField_management(sexProportions,"CALC_ATOTPOPBT","DOUBLE")
        except:
            pass
        arcpy.CalculateField_management(sexProportions,"CALC_ATOTPOPBT","!ATOTPOPMT!+!ATOTPOPFT!","PYTHON")
        # create table view to avoid division by 0
        vTable = os.path.basename(sexProportions) + "_VIEW"
        vExpression = '"CALC_ATOTPOPBT" > 0'
        arcpy.MakeTableView_management(sexProportions, vTable, vExpression)  
        # add prop fields and calculate
        mProp = "ATOTPOPMTPROP"
        try:
            arcpy.AddField_management(vTable,mProp,"DOUBLE")
        except:
            pass
        mCalc = "float(!ATOTPOPMT!)/float(!CALC_ATOTPOPBT!)"
        arcpy.CalculateField_management(vTable,mProp,mCalc,"PYTHON")
        fProp = "ATOTPOPFTPROP"
        try:
            arcpy.AddField_management(vTable,fProp,"DOUBLE")
        except:
            pass
        fCalc = "float(!ATOTPOPFT!)/float(!CALC_ATOTPOPBT!)"
        arcpy.CalculateField_management(vTable,fProp,fCalc,"PYTHON")
        # create table view to fill in nulls
        # define view
        view0 = os.path.basename(sexProportions) + "_NULL"
        # define calculation expression
        expression0 = '"CALC_ATOTPOPBT" <= 0' 
        arcpy.MakeTableView_management(sexProportions, view0, expression0)
        arcpy.CalculateField_management(view0, mProp, "0", "PYTHON")
        arcpy.CalculateField_management(view0, fProp, "0", "PYTHON")
        propFields = [mProp,fProp]
        return (1,sexProportions,propFields)
    except:
        return (0,inSexTable,arcpy.GetMessages())
    

def calculateAgeProportions(ageIn):
    arcpy.env.overwriteOutput=True
    returnList = []
    # calculate the proportions
    ageProportions = ageIn + "_proportions"
##    return ageProportions
    arcpy.CopyRows_management(ageIn,ageProportions)
    # add CALC_ATOTPOPBT
    try:
        arcpy.AddField_management(ageProportions,"CALC_ATOTPOPBT","DOUBLE")
    except:
        pass
    # parse the calculation expression
    ageExpression = "!A000_004BT! + !A005_009BT! + !A010_014BT! + !A015_019BT! + !A020_024BT! + !A025_029BT! + !A030_034BT! + !A035_039BT! + !A040_044BT! + !A045_049BT! + !A050_054BT! + !A055_059BT! + !A060_064BT! + !A065_069BT! + !A070_074BT! + !A075_079BT! + !A080_084BT! + !A085_089BT! + !A090_094BT! + !A095_099BT! + !A100_104BT! + !A105_109BT! + !A110_114BT! + !A115_119BT!"
    # calculate the denominators
    denominator = "CALC_ATOTPOPBT"
    arcpy.CalculateField_management(ageProportions,denominator,ageExpression,"PYTHON")
    return arcpy.GetMessages()
    procVars = getSearchFields(ageIn)
    procVars.pop(0)
    procVars.sort()
    propFields = []
    # create table view to avoid division by 0
    vTable = os.path.basename(ageProportions) + "BT"
    vExpression = '"' + denominator + '"' + ' > 0'
    arcpy.MakeTableView_management(ageProportions, vTable, vExpression)  
    for procVar in procVars:
        try:
            # add prop fields and calculate
            cProp = procVar + "PROP"
            try:
                arcpy.AddField_management(vTable,cProp,"DOUBLE")
            except:
                pass
            cCalc = "float(!" + procVar +"!)/!" + denominator + "!"
            arcpy.CalculateField_management(vTable,cProp,cCalc,"PYTHON")
            # create table view to fill in nulls
            # define view
            view0 = os.path.basename(ageProportions) + procVar + "_NULL"
            # define calculation expression
            expression0 = '"' + denominator + '"' + '<= 0'
            arcpy.MakeTableView_management(ageProportions, view0, expression0)
            if int(arcpy.GetCount_management(view0)[0])>0:
                arcpy.CalculateField_management(view0, cProp, 0, "PYTHON")
            propFields.append(cProp)
        except:
            return (0,procVar,arcpy.GetMessages())
    propFields.sort()
    return (1,ageProportions,propFields)

            
def calculateAgeSexProportions(ageSex):
    arcpy.env.overwriteOutput=True
    returnList = []
    # calculate the proportions
    ageProportions = ageSex + "_proportions"
    arcpy.CopyRows_management(ageSex,ageProportions)
    # add CALC_ATOTPOPMT and CALC_ATOTPOPFT
    try:
        arcpy.AddField_management(ageProportions,"CALC_ATOTPOPMT","DOUBLE")
    except:
        pass
    try:
        arcpy.AddField_management(ageProportions,"CALC_ATOTPOPFT","DOUBLE")
    except:
        pass
    # list the fields in the table in order
    # to select those which are needed to
    # produce our denominator
    fields = getSearchFields(ageSex)
    fields.pop(0)
    # parse the calculation expression
    mExpression = "=!A000_004MT! + !A005_009MT! + !A010_014MT! + !A015_019MT! + !A020_024MT! + !A025_029MT! + !A030_034MT! + !A035_039MT! + !A040_044MT! + !A045_049MT! + !A050_054MT! + !A055_059MT! + !A060_064MT! + !A065_069MT! + !A070_074MT! + !A075_079MT! + !A080_084MT! + !A085_089MT! + !A090_094MT! + !A095_099MT! + !A100_104MT! + !A105_109MT! + !A110_114MT! + !A115_119MT!"

##    for field in fields:
##        if RepresentsInt(field[5:8])==True:
##            if int(field[1:4])<65:
##                if field[-2]=="M":
##                    if mExpression == "":
##                        mExpression = "!"+field+"!"
##                    else:
##                        mExpression = mExpression + " + !" + field + "!"
##    mExpression = mExpression + " + !A065PLUSMT!"
    fExpression = mExpression.replace("MT","FT")
    # calculate the denominators
    arcpy.CalculateField_management(ageProportions,"CALC_ATOTPOPMT",mExpression,"PYTHON")
    arcpy.CalculateField_management(ageProportions,"CALC_ATOTPOPFT",fExpression,"PYTHON")

    mFields = []
    fFields = []
    for field in fields:
        if field[-2]=="M":
            mFields.append(field)  
        else:
            fFields.append(field)
    mFields.sort()
    fFields.sort()
    processList = ["MT","FT"]
    propFields = []
    for processS in processList:
        if processS == "MT":
            procVars = mFields
            denominator = "CALC_ATOTPOPMT"
        else:
            procVars = fFields
            denominator = "CALC_ATOTPOPFT"
            
        # create table view to avoid division by 0
        vTable = os.path.basename(ageProportions) + processS
        vExpression = '"' + denominator + '"' + ' > 0'
        arcpy.MakeTableView_management(ageProportions, vTable, vExpression)  
        for procVar in procVars:
            try:
                # add prop fields and calculate
                cProp = procVar + "PROP"
                try:
                    arcpy.AddField_management(vTable,cProp,"DOUBLE")
                except:
                    pass
                cCalc = "float(!" + procVar +"!)/!" + denominator + "!"
                arcpy.CalculateField_management(vTable,cProp,cCalc,"PYTHON")
                # create table view to fill in nulls
                # define view
                view0 = os.path.basename(ageProportions) + procVar + "_NULL"
                # define calculation expression
                expression0 = '"' + denominator + '"' + '<= 0'
                arcpy.MakeTableView_management(ageProportions, view0, expression0)
                if int(arcpy.GetCount_management(view0)[0])>0:
                    arcpy.CalculateField_management(view0, cProp, 0, "PYTHON")
                propFields.append(cProp)
            except:
                return (0,procVar, arcpy.GetMessages())
    propFields.sort()
    return (1,ageProportions,propFields)

def getVariableDict(params):
    tbl = params[0]
    searchFields = params[1]
    varDict = {}
    with arcpy.da.SearchCursor(tbl,searchFields) as rows:
        for row in rows:
            USCID = row[0]
            varDict[USCID]= row
    return varDict

def getSearchFields(tbl):
    searchFields = []
    # generate the searchFields List
    sfs = arcpy.ListFields(tbl,"A*")
    sfNames = [sf.name for sf in sfs if sf.name[:3]<>"ANR"]
    for sfName in sfNames:
        searchFields.append(sfName)
    # grab a row from the tbl and throw out
    # the columns which have None data
    popList = []
    with arcpy.da.SearchCursor(tbl,sfNames) as rows:
        for row in rows:
            index = 0
            for value in row:
                if value == None:
                    popList.append(index)
                    index+=1
                else:
                    index+=1
            break
    popList.sort(reverse=True)
    for popItem in popList:
        searchFields.pop(popItem)
    searchFields.sort()
    searchFields = ["USCID"] + searchFields
    return searchFields
    
def process(gdb):
    processTime = datetime.datetime.now()
    returnList = []
    try:
        arcpy.env.workspace = gdb
        iso = os.path.basename(gdb)[:-4].lower()
        if iso == 'vcs':
            returnList.append("VCS does not have variables data")
            return returnList
        # grab the lookup table
        lookupTable = arcpy.ListTables("*lookup")[0]
        # parse the admin level and year
        tableSplit = lookupTable.split("_")
        admin = tableSplit[1]
        adminNum = int(admin[-1])
        year = tableSplit[2]
        # check for previous runs and clean up if needed
        proportionTbls = arcpy.ListTables("*" + admin + "*proportions")
        if len(proportionTbls)>0:
            for proportionTbl in proportionTbls:
                arcpy.Delete_management(proportionTbl)
        #MISSPELLED AND FIXED< CLEAN UP ONCE
        poportionTbls = arcpy.ListTables("*" + admin + "*poportions")
        if len(poportionTbls)>0:
            for poportionTbl in poportionTbls:
                arcpy.Delete_management(poportionTbl)

        # grab the age, group, age/sex,and estimates tables
        ageIn = gdb + os.sep + iso +"_" + admin + "_" + year + "_age_group"
        sexIn = gdb + os.sep + iso +"_" + admin + "_" + year + "_sex"
        age_sexIn = gdb + os.sep + iso +"_" + admin + "_" + year + "_age_sex_group"
        estimatesIn = gdb + os.sep + iso +"_" + admin + "_" + year + "_estimates"

        # COMMENTED THIS CHECK AS THEY ALL EXIST (US NOT EVALUATED) 2-7-17
        # check that they each exist
##        existList = [ageIn,sexIn,age_sexIn,estimatesIn]
##        for tbl in existList:
##            if arcpy.Exists(tbl):
##                continue
##            else:
##                returnList.append(iso + " is missing this table: " + tbl)
##        return returnList

        # calculate proportion
        try:
            ageProportionsCalc = calculateAgeProportions(ageIn)
            return (iso + ' check age proportions calculation', ageProportionsCalc)
        except:
            return (iso + ' error: on age proportions calculation', ageProportionsCalc)
        if ageProportionsCalc[0]==0:
            return ageProportionsCalc
        ageProportions = ageProportionsCalc[1]
        agePropFields = ageProportionsCalc[2]
##        return ageProportionsCalc
        try:
            sexProportionsCalc = calculateSexProportions(sexIn)
        except:
            return (iso + ' error: on sex proportions calculation')
        if sexProportionsCalc[0]==0:
            return sexProportionsCalc
##        return sexProportionsCalc
        sexProportions = sexProportionsCalc[1]
        sexPropFields = sexProportionsCalc[2]
        try:
            age_sexProportionsCalc = calculateAgeSexProportions(age_sexIn)
##        return age_sexProportionsCalc
        except:
            return (iso + ' error: on age/sex proportions calculation')
        if age_sexProportionsCalc[0]==0:
            return age_sexProportionsCalc
        age_sexProportions = age_sexProportionsCalc[1]
        age_sexPropFields = age_sexProportionsCalc[2]
        # all of the tables can be related by the field "USCID",
        # but the variables are unique to each table.
        # since all variable names start with "A" we can grab them
        # the estimates table is a special case where all we need is "USCID","E_ATOTPOPBT_2010"
        estimatesSearchFields = ["USCID","E_ATOTPOPBT_2010"]
        # read the files into dictionaries
        try:
            estimatesDict = getVariableDict((estimatesIn,estimatesSearchFields))
##            for key, value in estimatesDict.iteritems():
##                return (key,value)
        except:
            return (iso + ' error reading estimates dictionary dictionary')
        try:
            agePropDict = getVariableDict((ageProportions,["USCID"]+ agePropFields))
        except:
            return (iso + ' error reading age proportions dictionary')
        try:
            sexPropDict = getVariableDict((sexProportions,["USCID"]+ sexPropFields))
        except:
            return (iso + ' error reading sex proportions dictionary')
        try:
            age_sexPropDict = getVariableDict((age_sexProportions,["USCID"]+age_sexPropFields))
        except:
            return (iso + ' error reading age/sex proportions dictionary')
        # apply the proportions to the estimates table
        ageSearchFields = getSearchFields(ageIn)
##        return [ageSearchFields,agePropFields]
        sexSearchFields = getSearchFields(sexIn)
        age_sexSearchFields = getSearchFields(age_sexIn)
        try:
            estimates_with_sex = applyProportions(estimatesIn,estimatesDict,sexSearchFields, sexPropDict,0)
            if estimates_with_sex[0]==0:
                return (iso + ' error applying sex proportions',estimates_with_sex)
        except:
            return (iso + ' error applying sex proportions')
        # need to grab sexEstimatesDict now that they have been calculated.
        sexEstimatesSearchFields = ["USCID","E_ATOTPOPMT_2010","E_ATOTPOPFT_2010"]
        # read the files into dictionaries
        try:
            sexEstimatesDict = getVariableDict((estimatesIn,sexEstimatesSearchFields))
##            for key, value in sexEstimatesDict.iteritems():
##                return (key,value)
        except:
            return (iso + ' error reading estimates dictionary dictionary')
        
        # back to applying proportions
        try:
##            return (estimatesIn,ageSearchFields)
            estimates_with_age = applyProportions(estimatesIn,estimatesDict,ageSearchFields, agePropDict,0)
    ##        return estimates_with_age
            if estimates_with_age[0]==0:
                return (iso + ' error applying age proportions',estimates_with_age)
        except:
            return (iso + ' error applying age proportions')
        
        try:
            estimates_with_age_sex = applyProportions(estimatesIn,sexEstimatesDict,age_sexSearchFields, age_sexPropDict,1)
##            return estimates_with_age_sex
            if estimates_with_age_sex[0]==0:
                return (iso + ' error applying age/sex proportions',estimates_with_age_sex)
        except:
            return (iso + ' error applying age/sex proportions')
        
        # finally summarize the atotpopbt and the estimates fields national
        try:
            summaryTable = estimatesIn + "_summary"
            summaryFields = [["ISO","FIRST"],["ATOTPOPBT","SUM"]]
            summaryParams = arcpy.ListFields(estimatesIn,"E_*")
            for summaryParam in summaryParams:
                summaryFields.append([summaryParam.name,"SUM"])
            arcpy.env.overwriteOutput=True
            arcpy.Statistics_analysis(estimatesIn,summaryTable,summaryFields)
        except:
            return (iso + ' error creating summary table')
        returnList.append("Processed "+ iso + " " + str(datetime.datetime.now()-processTime))
            
    except:
        returnList.append("Error while processing " + iso + " " + str(datetime.datetime.now()-processTime))
        returnList.append(arcpy.GetMessages())

    return returnList

def main():
    workspace = r'D:\gpw\release_4_1\batch'
    arcpy.env.workspace = workspace
    procList = arcpy.ListWorkspaces("*")
    print "processing"
    # must create procList
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
