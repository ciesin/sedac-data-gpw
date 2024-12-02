import arcpy, os

workspace = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\BRA\Ingest\Census\working.gdb'

arcpy.env.workspace = workspace

table = workspace + os.sep + "bra_2010_v3"

fields = arcpy.ListFields(table,"*_2010")

for field in fields:
    parse = field.name
    if len(parse)==11:
        pass
    elif parse[:6] == "TOTPOP":
        split = parse.split("_")
        newField = "ATOTPOP" + split[1]
        print newField
        try:
            arcpy.AddField_management(table,newField,"DOUBLE")
            print "Added " + newField
        except:
            print arcpy.GetMessages
        try:
            expression = "!" + parse + "!"
            arcpy.CalculateField_management(table,newField,expression,"PYTHON")
            print "Calculated " + newField
            arcpy.DeleteField_management(table,field)
        except:
            print arcpy.GetMessages()
    else:
        newField = parse.replace("_2010","")
        try:
            arcpy.AddField_management(table,newField,"DOUBLE")
            print "Added " + newField
        except:
            print arcpy.GetMessages
        try:
            expression = "!" + parse + "!"
            arcpy.CalculateField_management(table,newField,expression,"PYTHON")
            print "Calculated " + newField
            arcpy.DeleteField_management(table,parse)
        except:
            print arcpy.GetMessages()

    

    
        
    

    
        
    
