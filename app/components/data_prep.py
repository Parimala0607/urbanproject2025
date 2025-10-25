import pandas as pd
import numpy as np
import json
import pickle
from urllib.request import urlopen



## Data cleaning/handling
df = pd.read_csv('https://raw.githubusercontent.com/anenbergresearch/app-files/main/unified_data_SYK_Apr2025.csv')

def w_avg(df, values, weights):
    d = df[values]
    w = df[weights]
    return (d * w).sum() / w.sum()

## Filter df
ds= df.query('Year<2005') #subsetted data before 2005
da = df.query('Year>=2005') #subsetted data after 2005
##Find 0 values in 2000
s =df.query('Year ==2000 & NO2==0')
ds.loc[(ds['ID'].isin(s.ID)),('NO2')] =np.nan
ds.loc[(ds.ID ==923),('NO2')]=np.nan
##Dataframe to be passed to other pages
DFILT = pd.concat([ds,da]) #merged
DFILT_V2 = DFILT.copy()

# V2 column 
V2_COLUMN_MAPPING = {
    'PM': 'Pw_PM_V2',
    'NO2': 'Pw_NO2_V2',
    'O3': 'Pw_O3_V2',
    'CO2': 'CO2_V2'
}
V1_COLUMN_MAPPING = {
    'PM': 'Pw_PM',
    'NO2': 'Pw_NO2',
    'O3': 'Pw_O3',
    'CO2': 'CO2'
}



    
## Percent change calculation : % change between two 2-year moving averages    
def calculate_change(low,high,df,pol):
    lowb = low+1
    highb = high-1
    ldf= df.query('@low <=Year <=@lowb').groupby('CityCountry')[['Population',pol]].mean()
    hdf = df.query('@highb <=Year <=@high').groupby('CityCountry')[['Population',pol]].mean()
    return ((hdf[pol]-ldf[pol])/ldf[pol])*100

DF_CHANGE = DFILT.query('Year == 2019')[['CityCountry','Latitude','Longitude','Population','C40']].set_index('CityCountry') #empty template for percent change values
for i in ['Pw_PM', 'Pw_NO2','Pw_O3','CO2']:
    DF_CHANGE[i] = calculate_change(2010,2019,DFILT,i)
DF_CHANGE.reset_index(inplace=True) 

DF_CHANGE_V2 = DFILT.query('Year == 2019')[['CityCountry','Latitude','Longitude','Population','C40']].set_index('CityCountry') #empty template for percent change values
for i in ['Pw_PM_V2','Pw_NO2_V2','Pw_O3_V2','CO2_V2']:
    DF_CHANGE_V2[i] = calculate_change(2010,2019,DFILT,i)
DF_CHANGE_V2.reset_index(inplace=True) 





col_stats = ['Population','Pw_NO2','Pw_PM','Pw_O3','CO2','PAF_PM','PAF_NO2','PAF_O3','Cases_NO2','Cases_PM','Cases_O3','Rates_NO2','Rates_O3','Rates_PM'] #Column Selection
col_stats_v2 = ['Population','Pw_NO2_V2','Pw_PM_V2','Pw_O3_V2','CO2_V2'] #Column Selection


## Regional (country or state) summary statistics (min/max, population-weighted mean) 
def find_stats(dataframe, region, version):
    # Select appropriate columns based on version
    if version == '1':
        cols = col_stats
    else:  # version == '2'
        cols = col_stats_v2
    
    # Mean by region/year
    me = dataframe.groupby([region, 'Year']).mean(numeric_only=True)[cols].round(decimals=2)
    me.Population = me.Population.round(decimals=-3)
    me = me.reset_index()
    
    # Max by region/year
    ma = dataframe.groupby([region, 'Year']).max(numeric_only=True)[cols].round(decimals=2)
    ma.Population = me.Population
    ma = ma.reset_index()
    
    # Min by region/year
    mi = dataframe.groupby([region, 'Year']).min(numeric_only=True)[cols].round(decimals=2)
    mi.Population = me.Population
    mi = mi.reset_index()
    
    return me, ma, mi

MEAN, MAX, MIN = find_stats(DFILT, 'Country', '1')
MEAN_V2, MAX_V2, MIN_V2 = find_stats(DFILT_V2, 'Country', '2')



def get_column_name(version, metric, pollutant):
    # Version 2 only supports Concentration
    if version == '2':
        return V2_COLUMN_MAPPING.get(pollutant, pollutant + '_V2')
    
    # Version 1 mapping
    if metric == 'Concentration':
        return V1_COLUMN_MAPPING[pollutant]
    elif metric == 'PAF':
        return f'PAF_{pollutant}'
    elif metric == 'Cases':
        return f'Cases_{pollutant}'
    elif metric == 'Rates':
        return f'Rates_{pollutant}'
    
    # Default to concentration if no match
    return pollutant






## Data handling/cleaning for "States" tab
countries = ['United States','China','India'] #Country selection 
STATES_DF ={}
STATES_DF['United States'] = pd.read_csv('https://raw.githubusercontent.com/anenbergresearch/app-files/main/IDtoStateUnited%20States.csv')
GJSON={}
for i in ['India','China']:
    STATES_DF[i] = pd.read_csv('https://raw.githubusercontent.com/anenbergresearch/app-files/main/IDtoState'+i+'.csv')
    url = "https://raw.githubusercontent.com/anenbergresearch/app-files/main/states_" +i.lower()+".geojson"
    response = urlopen(url)
    GJSON[i]= json.loads(response.read())
id_dict={}

with open('./pages/geojs/chinadict.pickle', 'rb') as handle:
    id_dict['China'] = pickle.load(handle)
    
    
DF = {}
MEAN_DF = {}
STATS ={}

DF_V2 = {}
MEAN_DF_V2 = {}
STATS_V2 ={}

col_select = ['ID','City','C40','Year','Population','Pw_NO2','Pw_PM','Pw_O3','CO2','PAF_PM','PAF_NO2','PAF_O3','Cases_NO2','Cases_PM','Cases_O3','Rates_NO2','Rates_O3','Rates_PM']
col_select_v2 = ['ID','City','C40','Year','Population','Pw_NO2_V2','Pw_PM_V2','Pw_O3_V2','CO2_V2']

# V1 data preparation
for i in countries:
    DF[i] = DFILT.query('Country ==@i')[col_select]
    DF[i] = DF[i].merge(STATES_DF[i][['ID','State']], how='left',on='ID')
    if i =='China':
        DF[i] = DF[i][DF[i].State != '자강도']
        DF[i]["State"] = DF[i]["State"].apply(lambda x: id_dict[i][x])
    DF[i]['CityID'] = DF[i].City + ' (' +DF[i].ID.apply(int).apply(str) +')' #create column CityID with "CityName (ID)"
    mean_, max_, min_ = find_stats(DF[i],'State', '1') 
    STATS[i]={'mean':mean_,'min':min_,'max':max_}
    MEAN_DF[i] = DF[i].groupby('Year')[col_stats[1:]].mean().reset_index() 
# V2 data preparation
for i in countries:
    DF_V2[i] = DFILT_V2.query('Country ==@i')[col_select_v2]
    DF_V2[i] = DF_V2[i].merge(STATES_DF[i][['ID','State']], how='left',on='ID')
    if i =='China':
        DF_V2[i] = DF_V2[i][DF_V2[i].State != '자강도']
        DF_V2[i]["State"] = DF_V2[i]["State"].apply(lambda x: id_dict[i][x])
    DF_V2[i]['CityID'] = DF_V2[i].City + ' (' +DF_V2[i].ID.apply(int).apply(str) +')' #create column CityID with "CityName (ID)"
    mean_, max_, min_ = find_stats(DF_V2[i],'State', '2') 
    STATS_V2[i]={'mean':mean_,'min':min_,'max':max_}
    MEAN_DF_V2[i] = DF_V2[i].groupby('Year')[col_stats_v2[1:]].mean().reset_index()
