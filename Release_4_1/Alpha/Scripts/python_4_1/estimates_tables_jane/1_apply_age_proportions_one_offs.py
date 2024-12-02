#Jane Mills
#5/12/17
#GPWv4
#Apply age/sex proportions (assume 2010 sex has already been calculated)

import arcpy, os, numpy, datetime
from arcpy import env
scriptTime = datetime.datetime.now()

rootFolder = r'D:\gpw\release_4_1\loading\processed'
isoList = ['prk']
gdbList = [os.path.join(rootFolder,iso+'.gdb') for iso in isoList]

for gdb in gdbList:
    template = r'D:\gpw\release_4_1\loading\processed_v2\ancillary.gdb\template'
    processTime = datetime.datetime.now()

    env.workspace = gdb
    iso = os.path.basename(gdb)[:-4]
    print iso
    
    #Find all our tables
    estList = arcpy.ListTables("*estimates")
    if len(estList) == 1:
        estimates = estList[0]
        admin = estimates[-16]
        propList = arcpy.ListTables("*admin"+admin+"_*age_sex_group_proportions")
        if len(propList) == 1:
            proportions = propList[0]

            print iso+": found all tables"

    try:
        #write estimates into memory
        estMem = 'in_memory' + os.sep + iso
        arcpy.CopyRows_management(template,estMem)
        arcpy.Append_management(estimates,estMem,"NO_TEST")

        #Fix estimates (switch male and female groups)
        arcpy.AlterField_management(estMem,"E_ATOTPOPFT_2010","male_temp")
        arcpy.AlterField_management(estMem,"E_ATOTPOPMT_2010","E_ATOTPOPFT_2010","E_ATOTPOPFT_2010")
        arcpy.AlterField_management(estMem,"male_temp","E_ATOTPOPMT_2010","E_ATOTPOPMT_2010")

        #Loop through male and female
        for sex in ['F','M']:
            #Add all necessary fields
            propFields = [f.name for f in arcpy.ListFields(proportions,"A*"+sex+"T_PROP")]
            estFields = []
            for field in propFields:
                estFields.append("E_"+field[:-4]+"2010")
                arcpy.AddField_management(estMem,"E_"+field[:-4]+"2010","DOUBLE")

            propFields.append("USCID")
            estFields.append("E_ATOTPOP"+sex+"T_2010")
            estFields.append("USCID")

            #Build dictionary of proportions values
            propDict = {}
            with arcpy.da.SearchCursor(proportions,propFields) as cursor:
                for row in cursor:
                    propDict[row[-1]] = row[:-1]

            #Fill out age fields (apply proportions)
            with arcpy.da.UpdateCursor(estMem,estFields,"E_ATOTPOPBT_2010 IS NOT NULL") as cursor:
                for row in cursor:
                    props = propDict[row[-1]]
                    total = row[-2]
                    row[:-2] = list(numpy.array(props)*total)
                    cursor.updateRow(row)

            del propDict

        #copy final estimates table to disk
        outTable = estimates+"_reprocessed"
        arcpy.CopyRows_management(estMem,outTable)
        del estMem
        print iso+": success"

    except:
        print iso+": failure"


print "Script Complete in " + str(datetime.datetime.now()-scriptTime)

