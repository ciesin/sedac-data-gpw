#Jane Mills
#3/29/2017
#Export everything to csv and gdb

# Import Libraries
import arcpy, os

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids_data\country_data.gdb'
template = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids_data\ancillary.gdb\template'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids_data\merged_data.gdb'

regionList = ['Africa','Asia','Europe','North_America','Oceania','South_America']
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
                ['arg','bol','bra','chl','col','ecu','flk','guf','guy','per','pry','sgs','sur','ury','ven']]

for i in range(len(regionList)):
    region = regionList[i]
    print region
    isoList = countryLists[i]

    #copy template, delete UBID
    outFC = os.path.join(outGDB,region+'_centroids')
    arcpy.CopyFeatures_management(template,outFC)
    arcpy.DeleteField_management(outFC,'UBID')

    #Add centroids to file
    for iso in isoList:
        print iso
        fcPath = os.path.join(centroids,iso+"_centroids")
        arcpy.Append_management(fcPath,outFC,"NO_TEST")


