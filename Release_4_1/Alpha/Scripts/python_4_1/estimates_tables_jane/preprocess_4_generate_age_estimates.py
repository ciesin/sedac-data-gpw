# apply variable proportions
# script generates proportions from age, sex, and age sex tables
import os, datetime
import multiprocessing
import arcpy
arcpy.env.overwriteOutput=True
scriptTime = datetime.datetime.now()

def calculateAgeSexProportions(inAgeSexTable):
    arcpy.env.overwriteOutput=True
    returnList = []
    age_sexProportions = inAgeSexTable + "_proportions"
    memTable = 'in_memory' + os.sep + os.path.basename(age_sexProportions)
    try:
        arcpy.CopyRows_management(inAgeSexTable,memTable)
##        return (0,arcpy.GetMessages())
        returnFields = []
        for sex in ['F','M']:
            sexFields = [f.name for f in arcpy.ListFields(memTable,"A*"+sex+"T")]
            #leave out anr and any fields without age categories
            fieldList = []
            propFields = []
            for f in sexFields:
                if not "ANR" in f:
                    if not "A000_014"+sex+"T" in f:
                        if not "A015_064"+sex+"T" in f:
                            with arcpy.da.SearchCursor(inAgeSexTable,f,'OBJECTID = 1') as cursor:
                                for row in cursor:
                                    if not row[0] is None and not f in fieldList:
                                        fieldList.append(f)                    
            fieldList.sort()
            # add CALC_ATOTPOPMT and CALC_ATOTPOPFT
            arcpy.AddField_management(memTable,"CALC_ATOTPOP"+sex+"T","DOUBLE")
            for f in fieldList:
                arcpy.AddField_management(memTable,f+"_PROP","DOUBLE")
                propFields.append(f+"_PROP")
            propFields.sort
            returnFields= returnFields + propFields
            searchFields = ["CALC_ATOTPOP"+sex+"T"] + fieldList + propFields
           
            #Calculate proportions
            try:
                with arcpy.da.UpdateCursor(memTable,searchFields) as urows:
                    for row in urows:
                        total=0
                        for i in range(len(row)):
                            value = row[i]
                            if value <> None:
                                total+=value
                        row[0] = total
                        j=0
                        try:
                            for i in range(len(row)):
                                try:
                                    value = row[i]
                                except:
                                    return (0,'Bad value')
                                if value == None:
                                    if j==0:
                                        j = i
                                    if total > 0:
                                        row[i] = row[i-j+1]/total
                                    else:
                                        row[i] = 0
                            urows.updateRow(row)
                        except:
                            return(0,"Error applying update: ")# + row)
            except:
                return (0,(memTable,searchFields))
         
        arcpy.CopyRows_management(memTable,age_sexProportions)
        return (1,age_sexProportions,returnFields)
    except:
        return (0,inAgeSexTable,arcpy.GetMessages())
        
def applyLLAgeSexProportions(age_sexProportions,propFields,outAgeSexTable,lookupDict):
    sexTable = outAgeSexTable.replace("age_sex_group","sex")
    iso = sexTable.split("_")[0]
    # read the table into a dict
    sexDict = {}
    try:
        with arcpy.da.SearchCursor(sexTable,["USCID","ATOTPOPMT","ATOTPOPFT"]) as lRows:
            for lRow in lRows:
                sexDict[lRow[0]]=(lRow[1],lRow[2])
    except:
        return (0, 'Failed on applying LL age_sex proportions, could not read sex totals into dictionary')
    # read the table into a dict
    apDict = {}
    try:  
        with arcpy.da.SearchCursor(age_sexProportions,['USCID']+propFields) as apRows:
            for apRow in apRows:
                lluscid = apRow[0]
                for index,pField in enumerate(propFields,1):
                    key = lluscid + "_" + pField
                    apDict[key]=apRow[index]
    except:
        return (0, 'Failed on applying age_sex proportions, could not read proportions into dictionary')
    # create inMemAgeSex
    inMemAgeSex = 'in_memory' + os.sep + os.path.basename(outAgeSexTable)
    templateAgeSex = r'D:\gpw\release_4_1\loading\templates.gdb\age_sex_group_template'
    arcpy.CopyRows_management(templateAgeSex,inMemAgeSex)
##    return (0, apDict.keys())
    try:
        # parse the insertFields
        insertAgeSexFields = ["ISO","USCID"] + [f.replace("_PROP","") for f in propFields]
        insertAgeSexCursor = arcpy.da.InsertCursor(inMemAgeSex, insertAgeSexFields)
        # iterate the sexDict
        for uscid, sexTuple in sexDict.iteritems():
            insertAgeSexList = [iso.upper(),uscid]
            atotpopmt = float(sexTuple[0])
            atotpopft = float(sexTuple[1])
##            return (0,sexTuple)
            # iterate propFields
            for propVar in propFields:
                # grab the lluscid from lookupDict
                if uscid in lookupDict.keys():
                    lluscid = lookupDict[uscid]
##                    return (0,uscid,lluscid)
                    propKey = lluscid + "_"+propVar
##                    return (0,propKey)
                    if propKey in apDict.keys():
                        ageProportion = apDict[propKey]
                    else:
                        ageProportion = 0
                else:
                    ageProportion = 0
                if propVar[-7]=="M":
                    popEst = atotpopmt
                    propCounter = 2
                elif propVar[-7]=="F":
                    popEst = atotpopft
                else:
                    return (0,propVar + " cannot determine M or F popEst")
                ageSexEst = popEst * ageProportion
                insertAgeSexList.append(ageSexEst)
##            return (0, propKey,apDict.keys(),insertAgeSexList)
            insertAgeSexTuple = tuple(insertAgeSexList)
            try:
                insertAgeSexCursor.insertRow(insertAgeSexTuple)
               
            except:
                return (0,insertAgeSexTuple)
        del insertAgeSexCursor
    except:
        return (0, 'Failed on applying age proportions, could not insert rows in inMemTable',
                (uscid,lluscid,atotpopmt,atotpopft,propKey,ageSexEst,insertAgeSexTuple),
                arcpy.GetMessages())
    # copy the table to disk
    arcpy.env.overwriteOutput = True
    arcpy.CopyRows_management(inMemAgeSex,outAgeSexTable)
    return (1,outAgeSexTable)
   
def applyAgeSexProportions(estimatesIn,estimatesDict,searchFields,propDict):
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
                    if estimatesDict[uscid][1] == None:
                        continue
                    elif estimatesDict[uscid][2] == None:
                        continue
                    atotpopmt = float(estimatesDict[uscid][1])
                    atotpopft = float(estimatesDict[uscid][2]) 
                except:
                    return (0,'could not get M/F pop', uscid, uscid in estimatesDict,estimatesDict[uscid])
                rowIndex = 0
                for value in urow:
                    if rowIndex == 0:
                        rowIndex+=1
                        continue
                    else:
                        analysisField = searchFields[rowIndex-1]
                        try:
                            propRow = propDict[uscid]
                            propValue = propRow[rowIndex]
##                            return (0,(propRow,propValue))
                            if analysisField[-2]=="M":
                                urow[rowIndex] = atotpopmt * propValue
                            elif analysisField[-2]=="F":
                                urow[rowIndex] = atotpopft * propValue
                            else:
                                return (0,("analysisField",analysisField))
                            rowIndex+=1
                        except:
                            return(0,'could not get M/F prop',uFields,urow,propRow,propValue)
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
        ageTables = arcpy.ListTables("*age_sex_group")
        # if the length of sexTables is 1 and sexAdmin is
        # admin of that table
##        return ageTables
        if len(ageTables)==1:
            ageAdmin = ageTables[0].split("_")[1]
            ageAdminNum = int(ageTables[0].split("_")[1][-1])
        else:
            # otherwise select the largest admin level
            adminIntList = []
            for ageTable in ageTables:
                adminIntList.append(int(ageTable.split("_")[1][-1]))
            ageAdminNum = max(adminIntList)
            ageAdmin = "admin"+str(ageAdminNum)
        # calculate the age proportions
        age_sexIn = os.path.join(gdb,arcpy.ListTables("*"+ageAdmin+"*age_sex_group")[0])
##        return age_sexIn
        try:
            age_sexProportionsCalc = calculateAgeSexProportions(age_sexIn)
        except:
            return (iso + ' error: age/sex proportions calculation')
        if age_sexProportionsCalc[0]==0:
            return age_sexProportionsCalc
        age_sexProportions = age_sexProportionsCalc[1]
        age_sexPropFields = age_sexProportionsCalc[2]
##        return (age_sexProportions, age_sexPropFields)
##        # read the files into dictionaries
##        try:
##            age_sexPropDict = getVariableDict((age_sexProportions,["USCID"]+ age_sexPropFields))
##        except:
##            return (iso + ' error reading age_sex proportions dictionary')
##        # if ageAdmin < admin the apply lower level data
##        if ageAdminNum < adminNum:
##            # define outSexTable
##            outAgeSexTable = iso + "_" + admin + "_" + year + "_age_sex_group"
##            # read the table into a dict
##            lookupDict = {}
##            if ageAdminNum == 0:
##                searchFields = ["USCID","NAME0"]
##            else:
##                searchFields = ["USCID","LLUSCID"]
##            with arcpy.da.SearchCursor(lookupTable,searchFields) as lRows:
##                for lRow in lRows:
##                    lookupDict[lRow[0]]=lRow[1]
##            try:
##                age_sexTableCalc = applyLLAgeSexProportions(age_sexProportions,age_sexPropFields, outAgeSexTable,lookupDict)
##                if age_sexTableCalc[0]==0:
##                    return (iso + ' error: on sex proportions application', age_sexTableCalc)
##                age_sexTable = age_sexTableCalc[1]
##                try:
##                    age_sexProportionsCalc = calculateAgeSexProportions(age_sexTable)
##                except:
##                    return (iso + ' error: age_sex proportions calculation')
##                if age_sexProportionsCalc[0]==0:
##                    return age_sexProportionsCalc
##                age_sexProportions = age_sexProportionsCalc[1]
##                age_sexPropFields = age_sexProportionsCalc[2]
##                # read the files into dictionaries
##                try:
##                    age_sexPropDict = getVariableDict((age_sexProportions,["USCID"]+ age_sexPropFields))
##                except:
##                    return (iso + ' error reading age_sex proportions dictionary')
##            except:
##                return (iso + ' error applying LL age_sex proportions', age_sexTableCalc)
##        return [f.replace("_PROP","") for f in age_sexPropFields]
##        # grab the estimates table
##        estimatesIn = gdb + os.sep + iso +"_" + admin + "_" + year + "_estimates"                    
##        estimatesSearchFields = ["USCID","E_ATOTPOPMT_2010","E_ATOTPOPFT_2010"]
##        # read the files into dictionaries
##        try:
##            estimatesDict = getVariableDict((estimatesIn,estimatesSearchFields))
##        except:
##            return (iso + ' error reading estimates dictionary dictionary')
##        try:
##            # grab the age_sex seachFields
##            age_sexSearchFields = [f.replace("_PROP","") for f in age_sexPropFields]
##            estimates_with_age_sex = applyAgeSexProportions(estimatesIn,estimatesDict,age_sexSearchFields,age_sexPropDict)
##            if estimates_with_age_sex[0]==0:
##                return (iso + ' error applying age_sex proportions',estimates_with_age_sex)
##            else:
##                estimatesOut = estimates_with_age_sex[1]
##        except:
##            return (iso + ' error applying age_sex proportions')
        returnList.append("Processed "+ estimatesOut + " " + str(datetime.datetime.now()-processTime))    
    except:
        returnList.append("Error while processing " + iso + " " + str(datetime.datetime.now()-processTime))
        returnList.append(arcpy.GetMessages())

    return returnList

def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    procList = arcpy.ListWorkspaces("bfa*")
    process(procList[0])
    print "processing"

    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
