# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 11:11:10 2018

@author: jmills
"""

values = ['4','8','12','16','20','24','28','31','32','36','40','44','48','50','51','52','56','60',
          '64','68','70','72','76','84','90','92','96','100','104','108','112','116','120','124',
          '132','136','140','144','148','152','156','158','170','174','175','178','180','184','188',
          '191','192','196','203','204','208','212','214','218','222','226','231','232','233','234',
          '238','242','246','248','250','254','258','262','266','268','270','275','276','288','292',
          '296','300','304','308','312','316','320','324','328','332','336','340','344','348','352',
          '356','360','364','368','372','376','380','384','388','392','398','400','404','408','410',
          '414','417','418','422','426','428','430','434','438','440','442','446','450','454','458',
          '462','466','470','474','478','480','484','492','496','498','499','500','504','508','512',
          '516','520','524','528','531','533','534','535','540','548','554','558','562','566','570',
          '574','578','580','583','584','585','586','591','598','600','604','608','612','616','620',
          '624','626','630','634','638','642','643','646','652','654','659','660','662','663','666',
          '670','674','678','682','686','688','690','694','702','703','704','705','706','710','716',
          '724','728','729','732','740','744','748','752','756','760','762','764','768','772','776',
          '780','784','788','792','795','796','798','800','804','807','818','826','831','832','833',
          '834','840','850','854','858','860','862','876','882','887','894','902','903','904','905',
          '906','907','908','999']

colors = ['#B34040','#785023','#F7EFA1','#C2B63A','#B39E44','#BFB436','#F0E0B4','#FFB3BA','#38A800',
          '#CDF57A','#B59C59','#D6B22F','#B5B18F','#FFDBD4','#E8A8B3','#7AB6F5','#DBBC4B','#F5EA87',
          '#FFBEE8','#AAFF00','#E3D481','#BFB388','#E9FFBE','#004DA8','#F7EB79','#73DFFF','#FFEBBE',
          '#733838','#FF3D25','#BFB493','#C7846D','#AD0069','#C4A658','#BEFFFF','#DBCB37','#D4B239',
          '#E8CB38','#D9599E','#CFA836','#A5F57A','#CF0000','#E3428A','#E9FFBE','#F7F372','#D9CA96',
          '#F5D04C','#E8C656','#E3D759','#6699CD','#FFAA00','#1FB0FF','#C4C164','#E0D3AB','#BA9B34',
          '#BAB48C','#00A9E6','#00C5FF','#267300','#005CE6','#D1B054','#DBD0AF','#C4BA99','#897044',
          '#E6DCAE','#D9CB86','#D6B560','#FFA94F','#BDA368','#B85A44','#ABE600','#EBDCA9','#E8E06B',
          '#E3D9AF','#CD6666','#B3AB88','#D4B561','#99767B','#EDE772','#F0C53A','#BAA975','#FFAA00',
          '#93CEFA','#004C73','#D1CBA5','#DECF5B','#73DFFF','#DED666','#38CD66','#0070FF','#F5D833',
          '#00A9BF','#FFBEBE','#CCC899','#FFEBBE','#F5617A','#FFA77F','#A80047','#DB8A9E','#E0D6AB',
          '#730000','#895A44','#C2942B','#B3A05D','#FFBDD8','#FF6159','#FFBEBE','#EDE4AF','#FF0000',
          '#FFA7A8','#730000','#E03614','#B00000','#D6BD72','#DED56F','#EB8966','#B8B135','#CFC99D',
          '#EBCE81','#B58E0E','#C7BC65','#FF5500','#B3A069','#EBDD5E','#CD6699','#D4AC37','#C9AE42',
          '#CCBE60','#C7C230','#F5E0B0','#DBCDA7','#8CDFF2','#F7F37C','#F57A7A','#CDAA66','#D9D36C',
          '#73FFDF','#CCBE8B','#CCC297','#FF5566','#B59E43','#B89C5A','#FFA77F','#F5E0A6','#00C5D9',
          '#004DA8','#E3D6AF','#FAE7AA','#EBD798','#F2D866','#E9FFBE','#7AB6F5','#DBD0A0','#D1BD38',
          '#C4A658','#F7D46A','#DB8557','#F0D046','#DBC081','#DED445','#EBD84B','#FFBEBE','#004DA8',
          '#8CF57A','#B3E65E','#70A800','#D69DBC','#C7B740','#F5A27A','#894444','#EDD8A6','#F0B0CF',
          '#004DA8','#FF007B','#F5F1A2','#A87000','#FFDBB8','#F5E36C','#BAB272','#BDAB6A','#D6C356',
          '#DED795','#BEFFE8','#DED97A','#E0D3AD','#F2D65A','#CCC5A1','#D1C956','#C94444','#BDB56C',
          '#FAF6B1','#DBC786','#CCCAA1','#B8A75C','#E3C66F','#FF558F','#E8E268','#D4C344','#DBD59A',
          '#DBC140','#D79E7D','#F7D263','#BDB275','#B5AC86','#448970','#B8B440','#E6B53C','#C94820',
          '#CFC5A5','#E64C00','#FCBEC9','#FA578A','#B5B15C','#F7C334','#D1CA45','#6677CD','#FF0000',
          '#D9D4A5','#A80000','#FF9C8F','#D6D194','#CCBE99','#D1BB3D','#E69800','#EDDEB2','#E0D85C',
          '#D19059','#FAE9C0','#F5EE90','#DBD495','#C9B54D','#004DA8','#C2BF6D','#F5DF73','#9ED700',
          '#E65787','#A3FF73','#D4C49B','#C4AE31','#CD0066','#F7E44F','#B8A753','#CFC697','#F2ECBF',
          '#D9D5AD','#C9B142','#BDAC6A','#F0E76C','#CFB234']

names = ['Afghanistan','Albania','Algeria','American Samoa','Andorra','Angola','Antigua and Barbuda',
         'Azerbaijan','Argentina','Australia','Austria','Bahamas','Bahrain','Bangladesh','Armenia',
         'Barbados','Belgium','Bermuda','Bhutan','Bolivia (Plurinational State of)','Bosnia and Herzegovina',
         'Botswana','Brazil','Belize','Solomon Islands','British Virgin Islands','Brunei Darussalam',
         'Bulgaria','Myanmar','Burundi','Belarus','Cambodia','Cameroon','Canada','Cape Verde','Cayman Islands',
         'Central African Republic','Sri Lanka','Chad','Chile','China','Taiwan','Colombia','Comoros','Mayotte',
         'Congo','Democratic Republic of the Congo','Cook Islands','Costa Rica','Croatia','Cuba','Cyprus',
         'Czech Republic','Benin','Denmark','Dominica','Dominican Republic','Ecuador','El Salvador',
         'Equatorial Guinea','Ethiopia','Eritrea','Estonia','Faeroe Islands','Falkland Islands (Malvinas)',
         'Fiji','Finland','Aland Islands','France','French Guiana','French Polynesia','Djibouti','Gabon',
         'Georgia','Gambia','State of Palestine','Germany','Ghana','Gibraltar','Kiribati','Greece','Greenland',
         'Grenada','Guadeloupe','Guam','Guatemala','Guinea','Guyana','Haiti','Holy See','Honduras',
         'China Hong Kong Special Administrative Region','Hungary','Iceland','India','Indonesia',
         'Iran (Islamic Republic of)','Iraq','Ireland','Israel','Italy',"Cote d'Ivoire",'Jamaica','Japan',
         'Kazakhstan','Jordan','Kenya',"Democratic People's Republic of Korea",'Republic of Korea',
         'Kuwait','Kyrgyzstan',"Lao People's Democratic Republic",'Lebanon','Lesotho','Latvia','Liberia',
         'Libya','Liechtenstein','Lithuania','Luxembourg','China Macao Special Administrative Region',
         'Madagascar','Malawi','Malaysia','Maldives','Mali','Malta','Martinique','Mauritania','Mauritius',
         'Mexico','Monaco','Mongolia','Republic of Moldova','Montenegro','Montserrat','Morocco','Mozambique',
         'Oman','Namibia','Nauru','Nepal','Netherlands','Curacao','Aruba','Sint Maarten (Dutch part)',
         'Bonaire Saint Eustatius and Saba','New Caledonia','Vanuatu','New Zealand','Nicaragua','Niger',
         'Nigeria','Niue','Norfolk Island','Norway','Northern Mariana Islands','Micronesia (Federated States of)',
         'Marshall Islands','Palau','Pakistan','Panama','Papua New Guinea','Paraguay','Peru','Philippines',
         'Pitcairn','Poland','Portugal','Guinea-Bissau','Timor-Leste','Puerto Rico','Qatar','Reunion',
         'Romania','Russian Federation','Rwanda','Saint-Barthelemy','Saint Helena','Saint Kitts and Nevis',
         'Anguilla','Saint Lucia','Saint-Martin (French part)','Saint Pierre and Miquelon',
         'Saint Vincent and the Grenadines','San Marino','Sao Tome and Principe','Saudi Arabia','Senegal',
         'Serbia','Seychelles','Sierra Leone','Singapore','Slovakia','Viet Nam','Slovenia','Somalia',
         'South Africa','Zimbabwe','Spain','South Sudan','Sudan','Western Sahara','Suriname',
         'Svalbard and Jan Mayen Islands','Swaziland','Sweden','Switzerland','Syrian Arab Republic',
         'Tajikistan','Thailand','Togo','Tokelau','Tonga','Trinidad and Tobago','United Arab Emirates',
         'Tunisia','Turkey','Turkmenistan','Turks and Caicos Islands','Tuvalu','Uganda','Ukraine',
         'The former Yugoslav Republic of Macedonia','Egypt','United Kingdom of Great Britain and Northern Ireland',
         'Guernsey','Jersey','Isle of Man','United Republic of Tanzania','United States of America',
         'United States Virgin Islands','Burkina Faso','Uruguay','Uzbekistan','Venezuela (Bolivarian Republic of)',
         'Wallis and Futuna Islands','Western Samoa','Yemen','Zambia','French Southern Territories','Bouvet Island',
         'Heard Island and McDonald Islands','British Indian Ocean Territory','South Georgia and the South Sandwich Islands',
         'Spratly Islands','United States Minor Outlying Islands','Kosovo']

line1 = '        <Rule>'
lines2 = ['          <Name>"','"</Name>']
lines3 = ['          <Title>','</Title>']
lines4 = ['          <Filter>','            <PropertyIsEqualTo>','              <PropertyName>Value</PropertyName>']
lines5 = ['              <Literal>','</Literal>']
lines6 = ['            </PropertyIsEqualTo>','          </Filter>                    ','          <PolygonSymbolizer>','            <Fill>']
lines7 = ['              <CssParameter name="fill">','</CssParameter>']
lines8 = ['              <CssParameter name="fill-opacity">1</CssParameter>','            </Fill>','            <Stroke>',
          '              <CssParameter name="stroke">#828282</CssParameter>','              <CssParameter name="stroke-width">0.2</CssParameter>','            </Stroke>',
          '          </PolygonSymbolizer>','        </Rule>']



for i in range(len(colors)):
    color = colors[i]
    name = names[i]
    value = values[i]
    
    print(line1)
    print(lines2[0]+name+lines2[1])
    print(lines3[0]+name+lines3[1])
    print(lines4[0])
    print(lines4[1])
    print(lines4[2])
    print(lines5[0]+value+lines5[1])
    print(lines6[0])
    print(lines6[1])
    print(lines6[2])
    print(lines6[3])
    print(lines7[0]+color+lines7[1])
    print(lines8[0])
    print(lines8[1])
    print(lines8[2])
    print(lines8[3])
    print(lines8[4])
    print(lines8[5])
    print(lines8[6])
    print(lines8[7])





