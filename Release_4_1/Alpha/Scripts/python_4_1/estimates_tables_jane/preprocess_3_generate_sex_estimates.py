# apply variable proportions
# script generates proportions from age, sex, and age sex tables
import os, datetime
import multiprocessing
import arcpy
arcpy.env.overwriteOutput=True
scriptTime = datetime.datetime.now()

def calculateSexProportions(inSexTable):
    arcpy.env.overwriteOutput=True
    returnList = []
    sexProportions = inSexTable + "_proportions"
    try:
        arcpy.CopyRows_management(inSexTable,sexProportions)
        # add CALCATOTPOPBT PROPMT and PROPFT
        if len(arcpy.ListFields(sexProportions,"CALC_ATOTPOPBT"))==0:
            arcpy.AddField_management(sexProportions,"CALC_ATOTPOPBT","DOUBLE")
        arcpy.CalculateField_management(sexProportions,"CALC_ATOTPOPBT","!ATOTPOPMT!+!ATOTPOPFT!","PYTHON")
        # create table view to avoid division by 0
        vTable = os.path.basename(sexProportions) + "_VIEW"
        vExpression = '"CALC_ATOTPOPBT" > 0'
        arcpy.MakeTableView_management(sexProportions, vTable, vExpression)  
        # add prop fields and calculate
        mProp = "ATOTPOPMTPROP"
        if len(arcpy.ListFields(vTable,mProp))==0:
            arcpy.AddField_management(vTable,mProp,"DOUBLE")
        mCalc = "float(!ATOTPOPMT!)/float(!CALC_ATOTPOPBT!)"
        arcpy.CalculateField_management(vTable,mProp,mCalc,"PYTHON")
        fProp = "ATOTPOPFTPROP"
        if len(arcpy.ListFields(vTable,fProp))==0:
            arcpy.AddField_management(vTable,fProp,"DOUBLE")
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
def applyLLSexProportions(sexProportions,outSexTable,lookupDict):
    # read the table into a dict
    spDict = {}
    try:
        with arcpy.da.SearchCursor(sexProportions,["USCID","ATOTPOPMTPROP","ATOTPOPFTPROP"]) as spRows:
            for spRow in spRows:
                lluscid = spRow[0]
                spDict[spRow[0]]=(spRow[1],spRow[2])
    except:
        return (0, 'Failed on applying sex proportions, could not read proportions into dictionary')
    totalTable = outSexTable.replace("sex","total")
    # read the table into a dict
    totalDict = {}
    try:
        with arcpy.da.SearchCursor(totalTable,["USCID","ATOTPOPBT"]) as lRows:
            for lRow in lRows:
                totalDict[lRow[0]]=lRow[1]
    except:
        return (0, 'Failed on applying sex proportions, could not read totals into dictionary')
    # create inMemSex
    inMemSex = 'in_memory' + os.sep + outSexTable
    templateSex = r'D:\gpw\release_4_1\loading\templates.gdb\sex_template'
    arcpy.CopyRows_management(templateSex,inMemSex)
    insertCursor = arcpy.da.InsertCursor(inMemSex, ["ISO","USCID","ATOTPOPMT","ATOTPOPFT"])
    # iterate the totalDict
    try:
        for uscid, atotpopbt in totalDict.iteritems():
            # grab the lluscid from the lookupDict
            if uscid in lookupDict:
                lluscid = lookupDict[uscid]
            else:
                return (0, ("USCID not in lookupDict",uscid,atotpopbt))
            # grab the prop values
##            return (0,spDict.keys())
            mProp = float(spDict[lluscid][0])
            fProp = float(spDict[lluscid][1])
            
            # estimate the values
            mEst = atotpopbt * mProp
            fEst = atotpopbt * fProp
            # insert a row into inMemSex
            iso = totalTable.split("_")[0]
            insertCursor.insertRow((iso.upper(),uscid,mEst,fEst))
        del insertCursor
    except:
        return (0, 'Failed on applying sex proportions, could not insert rows in inMemTable',(lluscid,mProp,fProp,mEst,fEst))
    # copy the table to disk
    arcpy.CopyRows_management(inMemSex,outSexTable)
    return (1,outSexTable)
def applySexProportions(estimatesIn,estimatesDict,searchFields,propDict,crossTabFlag):
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
                try:
                    updateRows.updateRow(urow)
                except:
                    return (0,uFields,urow)

        # copy the file back to disk and delete the in memory copy
        arcpy.CopyRows_management(inMemEst,estimatesIn)
        arcpy.Delete_management(inMemEst)
        return (1,estimatesIn)
    except:
        return (0,returnList,urow,arcpy.GetMessages())
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
def getVariableDict(params):
    tbl = params[0]
    searchFields = params[1]
    varDict = {}
    with arcpy.da.SearchCursor(tbl,searchFields) as rows:
        for row in rows:
            USCID = row[0]
            varDict[USCID]= row
    return varDict
    
def process(gdb):
    arcpy.env.overwriteOutput = True
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
        # list the sexTables
        sexTables = arcpy.ListTables("*sex")
        # if the length of sexTables is 1 and sexAdmin is
        # admin of that table
        if len(sexTables)==1:
            sexAdmin = sexTables[0].split("_")[1]
            sexYear = sexTables[0].split("_")[2]
        else:
            # otherwise select the largest admin level
            adminIntList = []
            for sexTable in sexTables:
                adminIntList.append(int(sexTable.split("_")[1][-1]))
            sexAdminNum = max(adminIntList)
            sexAdmin = "admin"+str(sexAdminNum)
        # calculate the sex proportions
        sexIn = gdb + os.sep + iso + "_" + sexAdmin + "_" + sexYear + "_sex"
        try:
            sexProportionsCalc = calculateSexProportions(sexIn)
        except:
            return (iso + ' error: sex proportions calculation')
        if sexProportionsCalc[0]==0:
            return sexProportionsCalc
        sexProportions = sexProportionsCalc[1]
        sexPropFields = sexProportionsCalc[2]
        # read the files into dictionaries
        try:
            sexPropDict = getVariableDict((sexProportions,["USCID"]+ sexPropFields))
        except:
            return (iso + ' error reading sex proportions dictionary')
        # grab the estimates table
        estimatesIn = gdb + os.sep + iso +"_" + admin + "_" + year + "_estimates"                    
        estimatesSearchFields = ["USCID","E_ATOTPOPBT_2010"]
        # read the files into dictionaries
        try:
            estimatesDict = getVariableDict((estimatesIn,estimatesSearchFields))
        except:
            return (iso + ' error reading estimates dictionary dictionary')
        # if sexAdmin < admin the apply lower level data
        if sexAdmin < admin:
            # define outSexTable
            outSexTable = iso + "_" + admin + "_" + year + "_sex"
            # read the table into a dict
            lookupDict = {}
            with arcpy.da.SearchCursor(lookupTable,["USCID","LLUSCID"]) as lRows:
                for lRow in lRows:
                    lookupDict[lRow[0]]=lRow[1]
            try:
                sexTableCalc = applyLLSexProportions(sexProportions,outSexTable,lookupDict)
                if sexTableCalc[0]==0:
                    return (iso + ' error: on sex proportions application', sexTableCalc)
                sexTable = sexTableCalc[1]
                try:
                    sexProportionsCalc = calculateSexProportions(sexTable)
                except:
                    return (iso + ' error: sex proportions calculation')
                if sexProportionsCalc[0]==0:
                    return sexProportionsCalc
                sexProportions = sexProportionsCalc[1]
                sexPropFields = sexProportionsCalc[2]
                # read the files into dictionaries
                try:
                    sexPropDict = getVariableDict((sexProportions,["USCID"]+ sexPropFields))
                except:
                    return (iso + ' error reading sex proportions dictionary')
            except:
                return (iso + ' error applying LL sex proportions', sexTableCalc)
        try:
            # grab the sex seachFields
            sexSearchFields = getSearchFields(sexIn)
            estimates_with_sex = applySexProportions(estimatesIn,estimatesDict,sexSearchFields,sexPropDict,0)
            if estimates_with_sex[0]==0:
                return (iso + ' error applying sex proportions',estimates_with_sex)
            else:
                estimatesOut = estimates_with_sex[1]
        except:
            return (iso + ' error applying sex proportions')
        returnList.append("Processed "+ estimatesOut + " " + str(datetime.datetime.now()-processTime))    
    except:
        returnList.append("Error while processing " + iso + " " + str(datetime.datetime.now()-processTime))
        returnList.append(arcpy.GetMessages())

    return returnList

def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    procList = arcpy.ListWorkspaces("bfa*")
    print "processing"
    process(procList[0])

    
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
