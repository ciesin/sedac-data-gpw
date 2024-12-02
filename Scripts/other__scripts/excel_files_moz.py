# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 10:24:42 2013

@author: kmacmanu
"""
import os
from copy import deepcopy
from xlrd import open_workbook
from xlutils.copy import copy as copy
import xlwt
from xlwt import Workbook

rootDir = r"\\Dataserver0\gpw\GPW4\InputData\Country\MOZ\census\census2007\Quadro 2. Populacao por area de residencia e sexo, segundo idade"
# list contents of rootDir
rootContents = os.listdir(rootDir)
# Create workbook
wb = xlwt.Workbook()
# add new sheet to the wb
ws = wb.add_sheet("data",cell_overwrite_ok=True)
# write the schema rows
ws.write(0,0,"USCID")
ws.write(0,1,"NAME3")
ws.write(0,2,"ATOTPOPBT")
ws.write(0,3,"ATOTPOPMT")
ws.write(0,4,"ATOTPOPFT")
ws.write(0,5,"ATOTPOPBU")
ws.write(0,6,"ATOTPOPMU")
ws.write(0,7,"ATOTPOPFU")
ws.write(0,8,"ATOTPOPBR")
ws.write(0,9,"ATOTPOPMR")
ws.write(0,10,"ATOTPOPFR")
ws.write(0,11,"NAME1")
ws.write(0,12,"NAME2")

# iterate the directories
rIndex = 0
n = 0
for provDir in rootContents:
    n = n + 1
    disDir = rootDir + os.sep + provDir + os.sep + "distritos"
    disContents = os.listdir(disDir)
    for disSub in disContents:
        disName = disSub.upper()
        district = disDir + os.sep + disSub
        districtContents = os.listdir(district)
        for posDir in districtContents:
            if posDir[-4:] == ".xls":
                pass
            else:
                posContents = os.listdir(district + os.sep + posDir)
                for posFile in posContents:
                    print posFile
                    rIndex = rIndex + 1
                    # open file of interest
                    rb = open_workbook(district + os.sep + posDir + os.sep + posFile, formatting_info=True)
                    # open sheet of interest 
                    sName = rb.sheet_names()[0]
                    rs = rb.sheet_by_name(sName)
                    uscid = sName
                    name3 = rs.cell_value(3,0)
                    ws.write(rIndex,0,uscid)
                    ws.write(rIndex,1,name3)
                    ws.write(rIndex,2,rs.cell_value(4,1))
                    ws.write(rIndex,3,rs.cell_value(4,2))
                    ws.write(rIndex,4,rs.cell_value(4,3))
                    ws.write(rIndex,5,rs.cell_value(4,4))
                    ws.write(rIndex,6,rs.cell_value(4,5))
                    ws.write(rIndex,7,rs.cell_value(4,6))
                    ws.write(rIndex,8,rs.cell_value(4,7))
                    ws.write(rIndex,9,rs.cell_value(4,8))
                    ws.write(rIndex,10,rs.cell_value(4,9))
                    ws.write(rIndex,11,provDir)
                    ws.write(rIndex,12,disName)
                   

# save to output xls
wb.save(rootDir + os.sep + "moz_rawTest.xls")    
            
            
        





    
