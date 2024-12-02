# Kytt MacManus
# December 2016
# create variable table templates

# read full list of variables and create
# table templates for the following categories:
##1) Total
##2) Age
##3) Sex
##4) UR
##5) Age x Sex
##6) Age x UR
##7) Sex x UR
##8) Age x Sex x UR
# Where single year age data exists these tables will
# be created for single year, and aggregated into 5
# year age groups

import arcpy, os
arcpy.env.overwriteOutput=True
variablesIn = r'D:\gpw\release_4_1\loading\templates.gdb\gpw4_variable_template'
# grab and create age tables
tableTypes = ["singleyear","group"]
crossTabs1 = ['age','age_sex','age_ur','age_sex_ur']
crossTabs2 = ['sex','sex_ur','ur','total']
crossTabs = crossTabs2#crossTabs1 + crossTabs2

##["FR","FU","FT","MR","MU","MT","BR","BU","BT"]
for crossTab in crossTabs:
    if crossTab in crossTabs1:
        for tableType in tableTypes:
            if tableType == "group":
                if crossTab == 'age':
                    variables = arcpy.ListFields(variablesIn,"A*_*BT")+arcpy.ListFields(variablesIn,"*PLUSBT")+arcpy.ListFields(variablesIn,"*NRBT")
                elif crossTab == 'age_sex':
                    variables = arcpy.ListFields(variablesIn,"A*_*MT")+arcpy.ListFields(variablesIn,"*PLUSMT")+arcpy.ListFields(variablesIn,"*NRMT")+arcpy.ListFields(variablesIn,"A*_*FT")+arcpy.ListFields(variablesIn,"*PLUSFT")+arcpy.ListFields(variablesIn,"*NRFT")
                elif crossTab == 'age_ur':
                    variables = arcpy.ListFields(variablesIn,"A*_*BU")+arcpy.ListFields(variablesIn,"*PLUSBU")+arcpy.ListFields(variablesIn,"*NRBU")+arcpy.ListFields(variablesIn,"A*_*BR")+arcpy.ListFields(variablesIn,"*PLUSBR")+arcpy.ListFields(variablesIn,"*NRBR")
                elif crossTab == 'age_sex_ur':
                    variables = arcpy.ListFields(variablesIn,"A*_*MU")+arcpy.ListFields(variablesIn,"*PLUSMU")+arcpy.ListFields(variablesIn,"*NRMU")+arcpy.ListFields(variablesIn,"A*_*MR")+arcpy.ListFields(variablesIn,"*PLUSMR")+arcpy.ListFields(variablesIn,"*NRMR")+arcpy.ListFields(variablesIn,"A*_*FU")+arcpy.ListFields(variablesIn,"*PLUSFU")+arcpy.ListFields(variablesIn,"*NRFU")+arcpy.ListFields(variablesIn,"A*_*FR")+arcpy.ListFields(variablesIn,"*PLUSFR")+arcpy.ListFields(variablesIn,"*NRFR")
                variableNames = [v.name for v in variables]
            else:
                if crossTab == 'age':
                    variables = arcpy.ListFields(variablesIn,"*BT")
                elif crossTab == 'age_sex':
                    variables = arcpy.ListFields(variablesIn,"*MT")+arcpy.ListFields(variablesIn,"*FT")
                elif crossTab == 'age_ur':
                    variables = arcpy.ListFields(variablesIn,"*BU")+arcpy.ListFields(variablesIn,"*BR")
                elif crossTab == 'age_sex_ur':
                    variables = arcpy.ListFields(variablesIn,"A*MU")+arcpy.ListFields(variablesIn,"A*MR")+arcpy.ListFields(variablesIn,"A*FU")+arcpy.ListFields(variablesIn,"A*FR")
                variableNames = [v.name for v in variables if v.name[4]<>'_' and v.name[:4]<>"ATOT"]
            templateTable = r'D:\gpw\release_4_1\loading\templates.gdb' + os.sep + crossTab + "_" + tableType + '_template'
            print templateTable
            arcpy.CreateTable_management(os.path.dirname(templateTable),os.path.basename(templateTable))
            arcpy.AddField_management(templateTable,"ISO","TEXT","#","#",10)
            arcpy.AddField_management(templateTable,"USCID","TEXT","#","#",255)
            arcpy.AddField_management(templateTable,"UBID","TEXT","#","#",255)
            for variableName in variableNames:
##                print variableName
##                break
                arcpy.AddField_management(templateTable,variableName,"DOUBLE")
            variables = None
    else:
        if crossTab == 'sex':
##            continue
            variables = arcpy.ListFields(variablesIn,"*TOTPOPMT")+arcpy.ListFields(variablesIn,"*TOTPOPFT")
        elif crossTab == 'sex_ur':
            variables = arcpy.ListFields(variablesIn,"*TOTPOPMU")+arcpy.ListFields(variablesIn,"*TOTPOPFU")+arcpy.ListFields(variablesIn,"*TOTPOPMR")+arcpy.ListFields(variablesIn,"*TOTPOPFR")
        elif crossTab == 'ur':
##            continue
            variables = arcpy.ListFields(variablesIn,"*TOTPOPBU")+arcpy.ListFields(variablesIn,"*TOTPOPBR")
        elif crossTab == 'total':
            variables = arcpy.ListFields(variablesIn,"*TOTPOPBT*")
        variableNames = [v.name for v in variables]
        templateTable = r'D:\gpw\release_4_1\loading\templates.gdb' + os.sep + crossTab +'_template'
        print templateTable
        arcpy.CreateTable_management(os.path.dirname(templateTable),os.path.basename(templateTable))
        arcpy.AddField_management(templateTable,"ISO","TEXT","#","#",10)
        arcpy.AddField_management(templateTable,"USCID","TEXT","#","#",255)
        arcpy.AddField_management(templateTable,"UBID","TEXT","#","#",255)
        arcpy.AddField_management(templateTable,"AGRID","TEXT","#","#",255)
        for variableName in variableNames:
##            print variableName
##            print "2"
##            break
            arcpy.AddField_management(templateTable,variableName,"DOUBLE")
        variables = None
