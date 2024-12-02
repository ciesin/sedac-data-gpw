#Jane Mills
#3/29/2017
#Export everything to csv and gdb

# Import Libraries
import arcpy, os, csv, osgeo
from osgeo import ogr

inDriver = ogr.GetDriverByName("ESRI Shapefile")
outDriver = ogr.GetDriverByName("GPKG")

root = r'D:\gpw\release_4_1\gpw-v410-centroids'
centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
template = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\ancillary.gdb\template'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\merged_data.gdb'
shpFolder = os.path.join(root,'shp')
csvFolder = os.path.join(root,'csv')
gpkgFolder = os.path.join(root,'gpkg')

regionList = ['Africa','Asia','Europe','North_America','Oceania','South_America',
              'USA_Midwest','USA_Northeast','USA_South','USA_West']
countryLists = [['ago','atf','bdi','ben','bfa','bvt','bwa','caf','civ','cmr','cod','cog','com','cpv',
                 'dji','dza','egy','eri','esh','eth','gab','gha','gin','gmb','gnb','gnq','hmd','ken',
                 'lbr','lby','lso','mar','mdg','mli','moz','mrt','mus','mwi','myt','nam','ner','nga',
                 'reu','rwa','sdn','sen','shn','sle','som','ssd','stp','swz','syc','tcd','tgo','tun',
                 'tza','uga','zaf','zmb','zwe'],
                ['afg','are','arm','aze','bgd','bhr','brn','btn','chn','cyp','geo','hkg','idn','ind',
                 'iot','irn','irq','isr','jor','jpn','kaz','kgz','khm','kor','kwt','lao','lbn','lka',
                 'mac','mdv','mmr','mng','mys','npl','omn','pak','phl','prk','pse','qat','sau','sgp',
                 'spr','syr','tha','tjk','tkm','tls','tur','twn','uzb','vnm','yem'],
                ['ala','alb','anr','aut','bel','bgr','bih','blr','che','cze','deu','dnk','esp','est',
                 'fin','fra','fro','gbr','ggy','gib','grc','hrv','hun','imn','irl','isl','ita','jey',
                 'kos','lie','ltu','lux','lva','mco','mda','mkd','mlt','mne','nld','nor','pol','prt',
                 'rou','rus','sjm','smr','srb','svk','svn','swe','ukr','vcs'],
                ['abw','aia','atg','bes','bhs','blm','blz','bmu','brb','can','cri','cub','cuw','cym',
                 'dma','dom','glp','grd','grl','gtm','hnd','hti','jam','kna','lca','maf','mex','msr',
                 'mtq','nic','pan','pri','slv','spm','sxm','tca','tto','umi','vct','vgb','vir'],
                ['asm','aus','cok','fji','fsm','gum','kir','mhl','mnp','ncl','nfk','niu','nru','nzl',
                 'pcn','plw','png','pyf','slb','tkl','ton','tuv','vut','wlf','wsm'],
                ['arg','bol','bra','chl','col','ecu','flk','guf','guy','per','pry','sgs','sur','ury','ven'],
                ['usaia','usaii','usail','usaks','usami','usamn','usamo','usand','usane','usaoh','usasd','usawi'],
                ['usact','usama','usame','usanh','usanj','usany','usapa','usari','usavt'],
                ['usaal','usaar','usadc','usade','usafl','usaga','usaky','usala','usamd','usams','usanc',
                 'usaok','usasc','usatn','usatx','usava','usawv'],
                ['usaak','usaaz','usaca','usaco','usahi','usaid','usamt','usanm','usanv','usaog','usaut',
                 'usawa','usawy']]

for i in range(2,len(regionList)):
    region = regionList[i]
    print region
    isoList = countryLists[i]

    #copy template, delete UBID
    outFC = os.path.join(outGDB,region+'_centroids')
    arcpy.CopyFeatures_management(template,outFC)
    arcpy.DeleteField_management(outFC,'UBID')

    #set up csv
    headers = ['GUBID','ISOALPHA','COUNTRYNM','NAME1','NAME2','NAME3','NAME4','NAME5','NAME6',
               'CENTROID_X','CENTROID_Y','INSIDE_X','INSIDE_Y','CONTEXT','CONTEXT_NM','WATER_CODE',
               'TOTAL_A_KM','WATER_A_KM','LAND_A_KM','UN_2000_E','UN_2005_E','UN_2010_E','UN_2015_E',
               'UN_2020_E','UN_2000_DS','UN_2005_DS','UN_2010_DS','UN_2015_DS','UN_2020_DS','B_2010_E',
               'F_2010_E','M_2010_E','A00_04B','A05_09B','A10_14B','A15_19B','A20_24B','A25_29B',
               'A30_34B','A35_39B','A40_44B','A45_49B','A50_54B','A55_59B','A60_64B','A65PLUSB','A65_69B',
               'A70PLUSB','A70_74B','A75PLUSB','A75_79B','A80PLUSB','A80_84B','A85PLUSB','A00_04F',
               'A05_09F','A10_14F','A15_19F','A20_24F','A25_29F','A30_34F','A35_39F','A40_44F','A45_49F',
               'A50_54F','A55_59F','A60_64F','A65PLUSF','A65_69F','A70PLUSF','A70_74F','A75PLUSF',
               'A75_79F','A80PLUSF','A80_84F','A85PLUSF','A00_04M','A05_09M','A10_14M','A15_19M','A20_24M',
               'A25_29M','A30_34M','A35_39M','A40_44M','A45_49M','A50_54M','A55_59M','A60_64M','A65PLUSM',
               'A65_69M','A70PLUSM','A70_74M','A75PLUSM','A75_79M','A80PLUSM','A80_84M','A85PLUSM']

    outcsv = os.path.join(csvFolder,region+'_centroids.csv')
    csvMem = csv.writer(open(outcsv,"wb"))
    csvMem.writerow(headers)

    #Add centroids to shapefile and csv
    for iso in isoList:
        print iso
        fcPath = os.path.join(centroids,iso+"_centroids")
            
        with arcpy.da.SearchCursor(fcPath,headers) as cursor:
            for row in cursor:
                csvMem.writerow(row)

        arcpy.Append_management(fcPath,outFC,"NO_TEST")

    #Save as gpkg
    outFile = os.path.join(gpkgFolder,region + '_centroids.gpkg')
    inDataSource = inDriver.Open(outFC,0)
    outData = outDriver.CreateDataSource(outFile)
    arcpy.FeatureClassToFeatureClass_conversion(outFC,outFile,region+"_centroids")

    #arcpy.FeatureClassToFeatureClass_conversion(outFC,outGDB,region+"_centroids")

    print 'saved geopackage'

