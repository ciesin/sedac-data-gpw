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
            if rawAdminNum < adminNum:
                # then this is the table fall all cases except irn, and swz
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
            procTable = ageSex
        else:
            procTable = False
        # parse the searchFields for use in determining appropriate codes
        if rawAdmin == 'admin0':
            searchFields = ['ISO']
            procSearchFields= ['ISO']
        elif rawAdmin == 'admin1':
            searchFields = ['USCID','UCADMIN0','UCADMIN1']
            procSearchFields = ['USCID']
        elif rawAdmin == 'admin2':
            searchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2']
            procSearchFields = ['USCID']
        elif rawAdmin == 'admin3':
            searchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2','UCADMIN3']
            procSearchFields = ['USCID']
        elif rawAdmin == 'admin4':
            searchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2','UCADMIN3','UCADMIN4']
            procSearchFields = ['USCID']
        elif rawAdmin == 'admin5':
            searchFields = ['USCID','UCADMIN0','UCADMIN1','UCADMIN2','UCADMIN3','UCADMIN4','UCADMIN5']
            procSearchFields = ['USCID']

        # read the lookupTable into a dict
        lookupDict = {}
        with arcpy.da.SearchCursor(lookupTable,searchFields) as lRows:
            for lRow in lRows:
                lookupDict[lRow[0]]=lRow
        # read the procTable and compare codes
        with arcpy.da.SearchCursor(procTable,procSearchFields) as sRows:
            for sRow in sRows:
                joinField = sRow[0]
                if not joinField in lookupDict:
##                    if RepresentsInt(joinField.split("_")[0]) == True:
##                        joinSplit = joinField.split("_")
                    return (joinField, joinField + " not in lookupDict for " + iso + " " + str(rawAdmin) + " the first key in lookupDict = " + next(iter(lookupDict)))
                else:
                    return 
        
        returnList.append([lookupTable,rawTable,sexTable,procTable])
##        returnList.append(str("Processed "+iso + " " + str(datetime.datetime.now()-processTime))
    except:
        returnList.append("Error while processing " + iso + " " + str(datetime.datetime.now()-processTime))
    return returnList
    
 

def main():
    print "processing"
    # must create procList
    procList = ['afg','ago','alb','are','arm','bfa',
                'bhr','blr','bwa','caf','can','chn',
                'civ','cod','col','cub','cuw','deu',
                'dji','dma','eri','fsm','gab','geo',
                'gha','gin','gmb','gnb','gnq','grc',
                'grd','guy','hti','ind','irn','irq',
                'jor','ken','kir','lbn','lbr','lby',
                'lux','mco','mdg','mhl','mli','mmr',
                'mng','mrt','msr','nam','nga','niu',
                'nru','nzl','png','prk','prt','qat',
                'rus','sau','sdn','sen','sle','smr',
                'som','swe','swz','syr','tca','tcd',
                'tha','tjk','tkl','tkm','tun','twn',
                'tza','uga','ukr','uzb','vnm','zmb']
##    procList = ['vnm']


    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        if result == None:
            continue
        if RepresentsInt(result[0].split("_")[0]) == True:
            continue
        else:
            print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
