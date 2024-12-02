import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()

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
        arcpy.AddField_management(sexProportions,"CALC_ATOTPOPBT","DOUBLE")
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
        expression0 = '"CALC_ATOTPOPBT" <= 0' 
        arcpy.MakeTableView_management(sexProportions, view0, expression0)
        arcpy.CalculateField_management(view0, mProp, "0", "PYTHON")
        arcpy.CalculateField_management(view0, fProp, "0", "PYTHON")
        propFields = [mProp,fProp]
        return (1,sexProportions,propFields)
    except:
        return (0,inSexTable,arcpy.GetMessages())

def calculateAgeSexProportions(ageSex):
    arcpy.env.overwriteOutput=True
    returnList = []
    # calculate the proportions
    ageProportions = ageSex + "_proportions"
    arcpy.CopyRows_management(ageSex,ageProportions)
    # add CALC_ATOTPOPMT and CALC_ATOTPOPFT
    arcpy.AddField_management(ageProportions,"CALC_ATOTPOPMT","DOUBLE")
    arcpy.AddField_management(ageProportions,"CALC_ATOTPOPFT","DOUBLE")
    # list the fields in the table in order
    # to select those which are needed to
    # produce our denominator
    fields = getSearchFields(ageSex)
    fields.pop(0)
    # parse the calculation expression
    mExpression = ""
    for field in fields:
        if RepresentsInt(field[5:8])==True:
            if int(field[1:4])<65:
                if field[-2]=="M":
                    if mExpression == "":
                        mExpression = "!"+field+"!"
                    else:
                        mExpression = mExpression + " + !" + field + "!"
    mExpression = mExpression + " + !A065PLUSMT!"
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
                arcpy.AddField_management(vTable,cProp,"DOUBLE")
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
def applySexProportions(input_parameters):
    # grab the sexProportions
    sexProportions = input_parameters[0]
    # read the table into a dict
    spDict = {}
    try:
        with arcpy.da.SearchCursor(sexProportions,["USCID","ATOTPOPMTPROP","ATOTPOPFTPROP"]) as spRows:
            for spRow in spRows:
                lluscid = spRow[0]
                spDict[spRow[0]]=(spRow[1],spRow[2])
    except:
        return (0, 'Failed on applying sex proportions, could not read proportions into dictionary')
    # grab the total table
    outSexTable = input_parameters[1]
    totalTable = outSexTable.replace("sex","total")
    # read the table into a dict
    totalDict = {}
    try:
        with arcpy.da.SearchCursor(totalTable,["USCID","ATOTPOPBT"]) as lRows:
            for lRow in lRows:
                totalDict[lRow[0]]=lRow[1]
    except:
        return (0, 'Failed on applying sex proportions, could not read totals into dictionary')
    # grab the lookupDict
    lookupDict = input_parameters[2]
    # create inMemSex
    inMemSex = 'in_memory' + os.sep + outSexTable
    templateSex = r'D:\gpw\release_4_1\loading\templates.gdb\sex_template'
    arcpy.CopyRows_management(templateSex,inMemSex)
    insertCursor = arcpy.da.InsertCursor(inMemSex, ["ISO","USCID","ATOTPOPMT","ATOTPOPFT"])
    # iterate the totalDict
    try:
        for uscid, atotpopbt in totalDict.iteritems():
            # grab the lluscid from the lookupDict
            lluscid = lookupDict[uscid]
            # grab the prop values
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


def applyAgeProportions(sexTable,ageProportions,propFields,outAgeSexTable,outAgeTable,lookupDict):
    propFields.sort()
##    return (0,propFields)
    # read sexTable into a dictionary
    iso = sexTable.split("_")[0]
    sexDict = {}
    try:
        with arcpy.da.SearchCursor(sexTable,["USCID","ATOTPOPMT","ATOTPOPFT"]) as sexRows:
            for sexRow in sexRows:
                uscid = sexRow[0]
                sexDict[sexRow[0]]=(sexRow[1],sexRow[2])
    except:
        return (0, 'Failed on applying sex proportions, could not read sex into dictionary')
    # read the table into a dict
    apDict = {}
    try:
        with arcpy.da.SearchCursor(ageProportions,["USCID"]+propFields) as apRows:
            for apRow in apRows:
                lluscid = apRow[0]
                for index,pField in enumerate(propFields,1):
                    key = lluscid + "_" + pField
                    apDict[key]=apRow[index]
    except:
        return (0, 'Failed on applying sex proportions, could not read proportions into dictionary')
    
    # create inMemAgeSex
    inMemAgeSex = 'in_memory' + os.sep + outAgeSexTable
    templateAgeSex = r'D:\gpw\release_4_1\loading\templates.gdb\age_sex_group_template'
    arcpy.CopyRows_management(templateAgeSex,inMemAgeSex)
    # create inMemAge
    inMemAge = 'in_memory' + os.sep + outAgeTable
    templateAge = r'D:\gpw\release_4_1\loading\templates.gdb\age_group_template'
    arcpy.CopyRows_management(templateAge,inMemAge)
    try:
        # parse the insertFields
        insertAgeSexFields = ["ISO","USCID"] + [f.replace("PROP","") for f in propFields]
        insertAgeFields = ["ISO","USCID"] + [f.replace("MTPROP","BT") for f in propFields if f[-6]=="M"]
        insertAgeSexCursor = arcpy.da.InsertCursor(inMemAgeSex, insertAgeSexFields)
        insertAgeCursor = arcpy.da.InsertCursor(inMemAge, insertAgeFields)
        # iterate the sexDict
        for uscid, sexTuple in sexDict.iteritems():
            insertAgeSexList = [iso.upper(),uscid]
            insertAgeList = [iso.upper(),uscid]
            atotpopmt = float(sexTuple[0])
            atotpopft = float(sexTuple[1])
            # iterate propFields
            for propVar in propFields:
                # grab the lluscid from lookupDict
                if uscid in lookupDict.keys():
                    lluscid = lookupDict[uscid]
                    propKey = lluscid + "_" + propVar
                    if propKey in apDict.keys():
                        ageProportion = apDict[propKey]
                    else:
                        ageProportion = 0
                else:
                    ageProportion = 0
                propCounter = 1
                if propVar[-6]=="M":
                    popEst = atotpopmt
                    propCounter = 2
                elif propVar[-6]=="F":
                    popEst = atotpopft
                else:
                    return propVar + " cannot determine M or F popEst"
                ageSexEst = popEst * ageProportion
                insertAgeSexList.append(ageSexEst)
                if (propCounter==1):
                    ageEst = ageSexEst
                else:
                    ageEst += ageSexEst
                if propCounter == 2:
                    insertAgeList.append(ageEst)
            insertAgeSexTuple = tuple(insertAgeSexList)
            insertAgeTuple = tuple(insertAgeList)
##            return (0, insertAgeFields, insertAgeTuple, insertAgeSexFields,insertAgeSexTuple)
            try:
                insertAgeSexCursor.insertRow(insertAgeSexTuple)
                insertAgeCursor.insertRow(insertAgeTuple)
##                return (0,'inserted')
            except:
                return (0,insertAgeSexTuple,insertAgeTuple)
        del insertAgeSexCursor
        del insertAgeCursor
    except:
        return (0, 'Failed on applying age proportions, could not insert rows in inMemTable',
                (uscid,lluscid,atotpopmt,atotpopft,propKey,ageSexEst,ageEst,insertAgeSexTuple,insertAgeTuple),
                arcpy.GetMessages())
    # copy the table to disk
    arcpy.env.overwriteOutput = True
    
    arcpy.CopyRows_management(inMemAgeSex,outAgeSexTable)
    arcpy.CopyRows_management(inMemAge,outAgeTable)
    return (1,outAgeTable,outAgeSexTable)
    
            

def process(iso):
    returnList = []
    processTime = datetime.datetime.now()
    try:
        gdb = r'D:\gpw\release_4_1\loading\processed' + os.sep + iso + '.gdb'
        arcpy.env.workspace = gdb
        # grab the lookup table
        lookupTable = arcpy.ListTables("*lookup")[0]
        # read the table into a dict
        lookupDict = {}
        with arcpy.da.SearchCursor(lookupTable,["USCID","LLUSCID"]) as lRows:
            for lRow in lRows:
                lookupDict[lRow[0]]=lRow[1]
        
        # parse the admin level and year
        tableSplit = lookupTable.split("_")
        admin = tableSplit[1]
        adminNum = int(admin[-1])
        year = tableSplit[2]
        # check for previous runs and clean up if needed
        proportionTbls = arcpy.ListTables("*proportions")
        if len(proportionTbls)>0:
            for proportionTbl in proportionTbls:
                delTable = proportionTbl.replace("_proportions","").replace(proportionTbl.split("_")[1],admin)
                arcpy.Delete_management(proportionTbl)
                if arcpy.Exists(delTable):
                    arcpy.Delete_management(delTable)
        
        # check for sexTable
        sexTable = iso + "_" + admin + "_" + year + "_sex"
        if not arcpy.Exists(sexTable):
            processSex = True
            outSexTable = sexTable
        else:
            # parse
            sexSplit = sexTable.split("_")
            sexAdmin = sexSplit[1]
            sexAdminNum = int(sexAdmin[-1])
            sexYear = sexSplit[2]
            processSex = False
        # list the rawTables and parse to select the ll data
        rawTables = arcpy.ListTables("*raw")
        for rawTable in rawTables:
            # parse
            rawSplit = rawTable.split("_")
            rawAdmin = rawSplit[1]
            rawAdminNum = int(rawAdmin[-1])
            rawYear = rawSplit[2]
            # look for the next lowest admin level
            if rawAdminNum < adminNum:
                # then this is the table for all cases except irn, and swz
                if iso == 'irn':
                    if rawAdminNum == 0:
                        break
                    else:
                        continue
                elif iso == 'swz':
                    if rawAdminNum == 1:
                        break
                    else:
                        continue
                else:
                    break
            else:
                continue
        
        # downscale the sexData
        if processSex == True:
            inSexTable = iso + "_" + rawAdmin + "_" + rawYear + "_sex"
##            return inSexTable
            try:
                sexProportionsCalc = calculateSexProportions(inSexTable)
                if sexProportionsCalc[0]==0:
                    return (iso + ' error: on sex proportions calculation')
                sexProportions = sexProportionsCalc[1]
            except:
                return (iso + ' error: on sex proportions calculation')
            try:
                sexTableCalc = applySexProportions((sexProportions,outSexTable,lookupDict))
                if sexTableCalc[0]==0:
                    return (iso + ' error: on sex proportions application', sexTableCalc)
                sexTable = sexTableCalc[1]
            except:
                return (iso + ' error applying sex proportions')
            # grab the age x sex table if it exists
            ageSex = iso + "_" + rawAdmin + "_" + rawYear + "_age_sex_group"
            if not arcpy.Exists(ageSex):
                return "There is no age x sex data for " + iso
        else:
            # grab the age x sex table if it exists
            ageSex = iso + "_" + admin + "_" + year + "_age_sex_group"
##            return ageSex
            if not arcpy.Exists(ageSex):
                ageSex2 = iso + "_" + rawAdmin + "_" + rawYear + "_age_sex_group"
                if not arcpy.Exists(ageSex2):
                    return "There is no age x sex data for " + iso
                else:
                    ageSex = ageSex2

        # downscale the ageSex data
        try:
            calcAgeProps = calculateAgeSexProportions(ageSex)
            if calcAgeProps[0]==0:
                return calcAgeProps
            ageProportions = calcAgeProps[1]
            propFields = calcAgeProps[2]
        except:
            return (iso + ' error: on age/sex proportions calculation')
##        return propFields
        # define output tables
        outAgeSexTable = iso + "_" + admin + "_" + year + "_age_sex_group"
        outAgeTable = iso + "_" + admin + "_" + year + "_age_group"
        try:
##            return applyAgeProportions(sexTable,ageProportions,propFields,outAgeSexTable,outAgeTable,lookupDict)
            appliedProps = applyAgeProportions(sexTable,ageProportions,propFields,outAgeSexTable,outAgeTable,lookupDict)
##            return appliedProps
            if appliedProps[0]==0:
                return appliedProps
            ageOut = appliedProps[1]
            ageSexOut = appliedProps[2]
        except:
            return (iso + ' error: on age/sex proportions application')
        
        try:
##            return ageOut
            # calculate broad age groups on ageOut
            # grab the fields to calculate
            cFields = arcpy.ListFields(ageOut,"A000_014*")+arcpy.ListFields(ageOut,"A015_064*")
            calcFields = [cField.name for cField in cFields]
            
            for calcField in calcFields:
                prefix = calcField[:-2]
                suffix = calcField[-2:]
                if prefix == "A000_014":
                    exp = "!A000_004" + suffix + "! + !A005_009" + suffix + "! + !A010_014" + suffix + "!"
                else:
                    exp = "!A015_019" + suffix + "! + !A020_024" + suffix + "! + !A025_029" + suffix + "! + !A030_034" + suffix + "! + !A035_039" + suffix + "! + !A040_044" + suffix + "! + !A045_049" + suffix + "! + !A050_054" + suffix + "! + !A055_059"+ suffix + "! + !A060_064" + suffix + "!"
                # complete the calculation
                try:
                    arcpy.CalculateField_management(ageOut,calcField,exp,"PYTHON")
                except:
                    returnList.append(arcpy.GetMessages())
        except:
            returnList.append(iso + " error calculating broad age categories")
        returnList.append(str("Processed "+iso + " " + str(datetime.datetime.now()-processTime)))
    except:
        returnList.append("Error while processing " + iso + " " + str(datetime.datetime.now()-processTime))
    return returnList
    
 

def main():
    print "processing"
    # must create procList
##    procList = ['afg','ago','alb','are','arm','bfa',
##                'bhr','blr','bwa','caf','can','chn',
##                'civ','cod','col','cub','cuw','deu',
##                'dji','dma','eri','fsm','gab','geo',
##                'gha','gin','gmb','gnb','gnq','grc',
##                'grd','guy','hti','ind','irn','irq',
##                'jor','ken','kir','lbn','lbr','lby',
##                'lux','mco','mdg','mhl','mli','mmr',
##                'mng','mrt','msr','nam','niu',
##                'nru','nzl','png','prk','prt','qat',
##                'rus','sau','sdn','sen','sle','smr',
##                'som','swe','swz','syr','tca','tcd',
##                'tha','tjk','tkl','tkm','tun','twn',
##                'tza','uga','ukr','uzb','vgb','vnm','zmb']
    procList = ['uga']#'ind']#,


    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        if result == None:
            continue
##        if RepresentsInt(result[0].split("_")[0]) == True:
##            continue
        else:
            print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
