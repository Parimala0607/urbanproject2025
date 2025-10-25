
CITY = [
    ["#E69F00", "#E69F00"],  # Orange
    ["#56B4E9", "#56B4E9"],  # Sky Blue
    ["#009E73", "#009E73"],  # Bluish Green
    ["#F0E442", "#F0E442"],  # Yellow
    ["#0072B2", "#0072B2"],  # Blue
    ["#D55E00", "#D55E00"],  # Vermillion
    ["#CC79A7", "#CC79A7"]   # Reddish Purple
]

MAP_COLORS= {'ocean':'#d7e8fc','land':'#123c69','lake':'white'}
#'#1e324a' '#d7e8fc' #FFF0C3
COLORSCALE =  [[0, '#21b504'],[0.5,'#fff70a'],
                              [1,'#c70f02']] #'RdYlGn_r'
CS ={'Concentration':[[0, '#21b504'],[0.5,'#fff70a'],
                              [1,'#c70f02']],'Rates':'YlOrRd',
                              'Cases':'YlOrRd','PAF':'YlOrRd'}
##Units for the different inputs
UNITS_conc={'CO2':'CO<sub>2</sub> (tonnes)','NO2': 'NO<sub>2</sub> (ppb)','O3':'O<sub>3</sub> (ppb)','PM': 'PM<sub>2.5</sub> (μg/m<sup>3</sup>)',"Population":'Population'}
UNITS_PAF ={'NO2': 'NO<sub>2</sub> (Population Attributable Fraction %)','O3':'O<sub>3</sub> (Population Attributable Fraction %)','PM': 'PM<sub>2.5</sub> (Population Attributable Fraction %)',"Population":'Population'}
UNITS_R ={'NO2': 'NO<sub>2</sub> (Attributable Pediatric Asthma Incidence/100K)','O3':'O<sub>3</sub> (Attributable Premature Deaths)','PM': 'PM<sub>2.5</sub> (Attributable Premature Deaths/100K)',"Population":'Population'}
UNITS_C = {'NO2': 'NO<sub>2</sub> (Attributable Pediatric Asthma Incidence)','O3':'O<sub>3</sub> (Attributable Premature Deaths)','PM': 'PM<sub>2.5</sub> (Attributable Premature Deaths)',"Population":'Population'}
UNITS = {'Concentration':UNITS_conc,'PAF':UNITS_PAF,'Rates':UNITS_R,'Cases':UNITS_C}

##Units for version 2
UNITS_conc_V2={'CO2':'CO<sub>2</sub> per capita (metric tonnes)','NO2': 'NO<sub>2</sub> (ppb)','O3':'O<sub>3</sub> (ppb)','PM': 'PM<sub>2.5</sub> (μg/m<sup>3</sup>)',"Population":'Population'}
UNITS_V2 = {'Concentration':UNITS_conc_V2,'PAF':UNITS_PAF,'Rates':UNITS_R,'Cases':UNITS_C}


UNITS_PC={'CO2':'Change in CO<sub>2</sub> (%)','NO2': 'Change in NO<sub>2</sub> (%)','O3':'Change in O<sub>3</sub> (%)','PM': 'Change in PM<sub>2.5</sub> (%)'}
UNITS_PC_V2={'CO2':'Change in CO<sub>2</sub> per capita (%)','NO2': 'Change in NO<sub>2</sub> (%)','O3':'Change in O<sub>3</sub> (%)','PM': 'Change in PM<sub>2.5</sub> (%)'}

#list of pollutants in the dataframe
POLS = ['O3','PM','NO2','CO2']

#settings for the display
DISP = {
    'background': 'white',
    'text': '#033c5a',
    'subtext': '#708090',
    'fades': '#6A8099',
}

FONTSIZE = 19
FONTFAMILY = 'Lato'
MEMBERS ={'Global Covenant of Mayors':['x','#76dfca'],'Breathe Life 2030':['star-triangle-up','#59a8d7'],'Climate Mayors (US ONLY)':['triangle-down','#3a6de5'],'Carbon Neutral Cities Alliance ':['diamond-wide','#ffa907'],'Resilient Cities Network':['hourglass','#d05d19'],'C40':['star','#ff0056']}

COUNTRY_SCATTER = {True:dict(name='C40',color = 'rgba(30, 49, 133,0.9)',symbol='star'),False:dict(name='Other Cities',color = 'rgba(76, 179, 145,0.8)',symbol='circle')}
