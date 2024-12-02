import os, shutil, itertools
import xlrd, xlwt
from xlutils.copy import copy
from fnmatch import fnmatch

root = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country'
pattern = "*.xlsx"

file_l = {}
errors = []

for path, subdirs, files in os.walk(root):
    for name in files:
        if fnmatch(name, pattern):
        	file_l.update({name: os.path.join(path,name)})

def new_convention(f_l):
    for k, v in f_l.iteritems():
        wdir = r'C:\Users\izhao\Desktop\trash'#raw_input("Enter local directory:")
        try:
            shutil.copy2(v, wdir)
            in_wb = xlrd.open_workbook(os.path.join(wdir, k), 'rb')  
            #copy to local folder for editing
            compass = []
            for sheet_index in range(in_wb.nsheets):
                temp = {}
                col_index = []
                sheet = in_wb.sheet_by_index(sheet_index)
                for col in range(sheet.ncols):
                    if "UCID" in sheet.cell(0, col).value:
                        col_index.append(col)
                        temp.update({sheet_index: col_index})
                if len(temp) > 0:
                    compass.append(temp)
            print compass
            wb = copy(in_wb)
            for nav in compass:
                sheet = wb.get_sheet(nav.keys()[0])
                for i in range(0, len(nav.values()[0])):
                    col = nav.values()[0][i]
                    sheet.write(0, col, 'UCADMIN'\
                                +in_wb.sheet_by_index(nav.keys()[0]).cell(0, col).value[-1])
            #finishi edits, move file back
    ##        if os.path.exists(v):
    ##            os.remove(v)
            wb.save("%s.xls"%v[:-5])
            print "%s.xls"%v[:-5]
        except:
            pass
    return


new_convention(file_l)
