import arcpy, os

workspace = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\BRA\Ingest\Census\working.gdb'

arcpy.env.workspace = workspace

table = workspace + os.sep + "bra_2010_v3"

cats = ["MT","FT","BT","MR","FR","BR","MU","FU","BU"]
nums = ["000_004","005_009","010_014","015_019","020_024"]
for cat in cats:
    for num in nums:
        if num == "000_004":
            expression = "!A000" + cat + "_2010!+!A001" + cat + "_2010!+!A002" + cat +"_2010!+!A003" + cat + "_2010!+!A004" + cat + "_2010!"
        elif num == "005_009":
            expression = "!A005" + cat + "_2010!+!A006" + cat + "_2010!+!A007" + cat +"_2010!+!A008" + cat + "_2010!+!A009" + cat + "_2010!"
        elif num == "010_014":
            expression = "!A010" + cat + "_2010!+!A011" + cat + "_2010!+!A012" + cat +"_2010!+!A013" + cat + "_2010!+!A014" + cat + "_2010!"
        elif num == "015_019":
            expression = "!A015" + cat + "_2010!+!A016" + cat + "_2010!+!A017" + cat +"_2010!+!A018" + cat + "_2010!+!A019" + cat + "_2010!"
        elif num == "020_024":
            expression = "!A020" + cat + "_2010!+!A021" + cat + "_2010!+!A022" + cat +"_2010!+!A023" + cat + "_2010!+!A024" + cat + "_2010!"
        else:
            print "error"
        newField = "A" + num + cat
        arcpy.AddField_management(table,newField,"DOUBLE")
        print "Added " + newField
        arcpy.CalculateField_management(table,newField,expression,"PYTHON")
        print "Calculated " + newField
