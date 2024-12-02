import arcpy,os
isos=["alb","are","arg","atg","bel",
      "bes","bfa","bhs","blr","cmr",
      "cod","col","cuw","cyp","dza",
      "egy","fji","fsm","gin","gmb",
      "gnb","gtm","guy","hrv","jpn",
      "ken","khm","kir","kos","ltu",
      "lux","mac","mco","mda","mex",
      "mhl","mli","mlt","mng","moz",
      "mrt","mtq","mus","myt","ncl",
      "ner","nga","nic","niu","nor",
      "nru","nzl","phl","rwa","sgp",
      "shn","slb","sur","svk","swe",
      "swz","sxm","tkl","tkm","ton",
      "tto","tun","tur","tuv","twn",
      "tza","vct","vir","vut","yem"]

for iso in isos:
    # check if a lookup exists, and if it does delete it
    arcpy.env.workspace = r'D:\gpw\release_4_1\loading\lookup_tables.gdb'
    if len(arcpy.ListTables(iso+"*"))==1:
        arcpy.Delete_management(arcpy.arcpy.ListTables(iso+"*")[0])
    # parse and copy in the new table
    inGDB = r'D:\gpw\4_0_prod\pop_tables' + os.sep + iso.lower() + '.gdb'
    arcpy.env.workspace = inGDB
    if len(arcpy.ListTables("*lookup*"))==0:
        inTbl = arcpy.ListTables("*total_pop_raw")[0]
    else:
        inTbl = arcpy.ListTables("*lookup*")[0]

    outTable = r'D:\gpw\release_4_1\loading\lookup_tables.gdb' + os.sep + iso + "_lookup"

    if not arcpy.Exists(outTable):
        arcpy.CopyRows_management(inTbl,outTable)
        print "Created " + outTable
    else:
        print outTable + " already exists"
                                
