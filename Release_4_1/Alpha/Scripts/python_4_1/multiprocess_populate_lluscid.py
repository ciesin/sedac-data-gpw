import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
def process(iso):
    arcpy.env.overwriteOutput=True
    returnList = []
    processTime = datetime.datetime.now()
    try:
        gdb = r'D:\gpw\release_4_1\loading\processed' + os.sep + iso + '.gdb'
        arcpy.env.workspace = gdb
        # grab the lookup table
        lookupTable = arcpy.ListTables("*lookup")[0]
        # parse the admin level and year
        tableSplit = lookupTable.split("_")
        admin = tableSplit[1]
        adminNum = int(admin[-1])
        year = tableSplit[2]
        # check for sexTable
        sexTable = iso + "_" + admin + "_" + year + "_sex"
        if not arcpy.Exists(sexTable):
            processSex = True
        else:
            # parse
            sexSplit = sexTable.split("_")
            sexAdmin = sexSplit[1]
            sexAdminNum = int(sexAdmin[-1])
            sexYear = sexSplit[2]
            processSex = False

        # list the rawTables and parse to select the correct one
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
        if processSex == True:
            sexTable = iso + "_" + rawAdmin + "_" + rawYear + "_sex"
            # parse
            sexSplit = sexTable.split("_")
            sexAdmin = sexSplit[1]
            sexAdminNum = int(sexAdmin[-1])
            sexYear = sexSplit[2]
        # grab the age x sex table if it exists
        ageSex = iso + "_" + rawAdmin + "_" + rawYear + "_age_sex_group"
        if arcpy.Exists(ageSex):
            procTable = rawTable
        else:
            procTable = False
##        return [iso,lookupTable,procTable]
        # parse the searchFields for use in determining appropriate codes
        atAdmin0 = False
        if rawAdmin == 'admin0':
            searchFields = ['USCID','ISO']
            procSearchFields = ['USCID','ISO']
##        else:
##            returnList.append(iso + " is not admin0")
##            return returnList
        elif rawAdmin == 'admin1':
            searchFields = ['USCID','UCADMIN0','UCADMIN1']
            procSearchFields = ['USCID','UCADMIN0','UCADMIN1']
        elif rawAdmin == 'admin2':
            searchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2']
            procSearchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2']
        elif rawAdmin == 'admin3':
            searchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2','UCADMIN3']
            procSearchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2','UCADMIN3']
        elif rawAdmin == 'admin4':
            searchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2','UCADMIN3','UCADMIN4']
            procSearchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2','UCADMIN3','UCADMIN4']
        elif rawAdmin == 'admin5':
            searchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2','UCADMIN3','UCADMIN4','UCADMIN5']
            procSearchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2','UCADMIN3','UCADMIN4','UCADMIN5']

        # read the lookupTable into a dict
        lookupDict = {}
        try:
            with arcpy.da.SearchCursor(lookupTable,searchFields) as lRows:
                for lRow in lRows:
                    llUScid = lRow[0]
                    if len(lRow)==2:
                        key = iso.upper()
                    else:
                        key = ""
                        lCounter = 0
                        for lData in lRow:
                            if lCounter == 0:
                                lCounter+=1
                                continue
                            elif key == "":
                                key = str(lData)
                            else:
                                key = key + "_" + str(lData)
                    lookupDict[key]=llUScid
        except:
            return [iso +  "problem with lookup table dict"]
        

        # read the procTable and compare codes
        procDict = {}
        with arcpy.da.SearchCursor(procTable,procSearchFields) as sRows:
            for sRow in sRows:
                if len(sRow)==2:
                    joinKey = iso.upper()
                else:
                    joinKey = ""
                    sCounter = 0
                    for sData in sRow:
                        if sCounter == 0:
                            sCounter+=1
                            continue
                        elif joinKey == "":
                            joinKey = str(sData)
                        else:
                            joinKey = joinKey + "_" + str(sData)
                    
                if not joinKey in lookupDict:
##                    if RepresentsInt(joinField.split("_")[0]) == True:
##                        joinSplit = joinField.split("_")
                    return [iso,rawAdmin,sRow,joinKey,lookupDict.keys()[0]]
                else:
                    procDict[joinKey]=sRow[0]
                    
        # copy the lookuptable into memory
        inMemLookup = 'in_memory' + os.sep + os.path.basename(lookupTable)
        arcpy.CopyRows_management(lookupTable,inMemLookup)
        # add LLUSCID
        arcpy.AddField_management(inMemLookup,"LLUSCID","TEXT")
        # update LLUSCID
        with arcpy.da.UpdateCursor(inMemLookup,searchFields+["POP_CONTEXT","LLUSCID"]) as uRows:
                for uRow in uRows:
                    if len(uRow)==4:
                        uKey = iso.upper()
                    else:
                        uKey = ""
                        uCounter = 0
                        for uData in uRow[0:-2]:
                            if uCounter == 0:
                                uCounter+=1
                                continue
                            elif uKey == "":
                                uKey = str(uData)
                            else:
                                uKey = uKey + "_" + str(uData)
                    if not uKey in procDict:
                        if uRow[-2]<>None:
                            continue
                        else:
                            return ['update error',iso,rawAdmin,uRow,uKey,lookupDict.keys()[0]]
                    else:
                        # grab uValue
                        uRow[-1] = procDict[uKey]
                        uRows.updateRow(uRow)
        # copy inMem back to disk
        
        arcpy.CopyRows_management(inMemLookup,gdb+os.sep+lookupTable)
        
##        returnList.append([lookupTable,rawTable,sexTable,procTable])
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
##                'tza','uga','ukr','uzb','vnm','zmb']
    procList = ['can','cod','ind','irq','nzl']


    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
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
