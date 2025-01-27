import dash
from dash import  dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.figure_factory as ff

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#C6C4C4"
}


# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


# path = "C:/Users/KD169FE/OneDrive - EY/Desktop/Call for  code/Application/"
raw_data = pd.ExcelFile("Call_for_code_Data.xlsx")
emis = pd.ExcelFile("emissions.xlsx")

app = dash.Dash(__name__) 

colors = {
    'background': '#fffcfc',
    'text': '#0c291f',
    'text1':'#000000'
}


emission_gas = {'Carbon dioxide (CO2)': 0,
                'Methane (CH4)': 1,
                'Nitrous oxide (N2O)': 2,
                'F-gases (Fluorinated)': 3}

stage = {'Land': 4,
         'Farm': 5,
         'Processing': 6,
         'Transport': 7,
         'Packaging': 8,
         'Retail': 9,
         'Consumer': 10,
         'Waste': 11}

st = {'Production':4,
     'Consumption':5,
     'Waste':6}

country_dict = {'CHINA':'China',
                'INDIA':'India',
                'JPN':'Japan',
                'US':'United States of America',
                'RUS':'Russian Federation',
                'BRAZIL':'Brazil'}
## create data 
df1 = pd.DataFrame()
for sheet in emis.sheet_names[2:]:
    emis_df = emis.parse(sheet_name = sheet)
    # so2 emissions for stated policy
    so2 = emis_df.iloc[6:11,:6].reset_index(drop=True)

    so2.columns = ["Industry","2018","2025","2030","2035","2040"]
    so2["Scenario"] = "Stated Policy"
    so2["Country"] = sheet
    so2["Emission"] = "SO2"

    # nox emissions for stated policy
    nox = emis_df.iloc[13:18,:6].reset_index(drop=True)

    nox.columns = ["Industry","2018","2025","2030","2035","2040"]
    nox["Scenario"] = "Stated Policy"
    nox["Country"] = sheet
    nox["Emission"] = "NOx"

    # pm emissions for stated policy
    pm = emis_df.iloc[20:25,:6].reset_index(drop=True)

    pm.columns = ["Industry","2018","2025","2030","2035","2040"]
    pm["Scenario"] = "Stated Policy"
    pm["Country"] = sheet
    pm["Emission"] = "PM"
    
    stated_policy = pd.concat([so2,nox,pm],ignore_index=True)
    
    # so2 emissions for current policy
    so2_current = emis_df.iloc[6:11,[12,1,13,14,15]].reset_index(drop=True)

    so2_current.columns = ["Industry","2018","2025","2030","2040"]
    so2_current["Scenario"] = "Current Policy"
    so2_current["Country"] = sheet
    so2_current["Emission"] = "SO2"

    # nox emissions for current policy
    nox_current = emis_df.iloc[13:18,[12,1,13,14,15]].reset_index(drop=True)

    nox_current.columns = ["Industry","2018","2025","2030","2040"]
    nox_current["Scenario"] = "Current Policy"
    nox_current["Country"] = sheet
    nox_current["Emission"] = "NOx"

    # pm emissions for current policy
    pm_current = emis_df.iloc[20:25,[12,1,13,14,15]].reset_index(drop=True)

    pm_current.columns = ["Industry","2018","2025","2030","2040"]
    pm_current["Scenario"] = "Current Policy"
    pm_current["Country"] = sheet
    pm_current["Emission"] = "PM"
    
    current_policy = pd.concat([so2_current,nox_current,pm_current],ignore_index=True)
    
    # so2 emissions for sustainable development policy
    so2_sus = emis_df.iloc[6:11,[12,1,20,21,22]].reset_index(drop=True)

    so2_sus.columns = ["Industry","2018","2025","2030","2040"]
    so2_sus["Scenario"] = "Sustainable Development"
    so2_sus["Country"] = sheet
    so2_sus["Emission"] = "SO2"

    # nox emissions for sustainable development policy
    nox_sus = emis_df.iloc[13:18,[12,1,20,21,22]].reset_index(drop=True)

    nox_sus.columns = ["Industry","2018","2025","2030","2040"]
    nox_sus["Scenario"] = "Sustainable Development"
    nox_sus["Country"] = sheet
    nox_sus["Emission"] = "NOx"

    # pm emissions for sustainable development policy
    pm_sus = emis_df.iloc[20:25,[12,1,20,21,22]].reset_index(drop=True)

    pm_sus.columns = ["Industry","2018","2025","2030","2040"]
    pm_sus["Scenario"] = "Sustainable Development"
    pm_sus["Country"] = sheet
    pm_sus["Emission"] = "PM"
    
    sus_policy = pd.concat([so2_sus,nox_sus,pm_sus],ignore_index=True)
    df = pd.concat([stated_policy,current_policy,sus_policy],ignore_index=True)
    df1 = pd.concat([df1,df],ignore_index=True)

df1 = df1.fillna(0)
df2 = df1.copy()
#print(df2.shape)
df1 = df1[df1["Country"].isin(list(country_dict.keys()))].reset_index(drop=True)
df1['Country'] = df1['Country'].map(country_dict)
df1 = df1.dropna()
#print(df1.shape)
## FOod dataframe
food_df = raw_data.parse(sheet_name="Food")
food_df2 = food_df.copy()
#print(food_df2.shape)
food_df = food_df[food_df["Country"].isin(list(country_dict.values()))].reset_index(drop=True)
#print(food_df.shape)
emissions_2015 = food_df[food_df["Year"]==food_df["Year"].max()]["GHG Emissions"].sum()
food_sunburst = round((food_df[food_df["Year"]==food_df["Year"].max()].
groupby(["Country","Food System Stage","GHG"])["GHG Emissions"].sum().
sort_values(ascending=False)/emissions_2015)*100,2). reset_index()
food_df["Stage"] = np.where(food_df["Food System Stage"].isin(["Land","Farm","Processing","Transport"])==True,"Production",
np.where(food_df["Food System Stage"].isin(["Packaging","Retail","Consumer"])==True,"Consumption",
food_df["Food System Stage"]))

heat_map = food_df2[(food_df2["Year"]==food_df2["Year"].max())&\
                  (food_df2['GHG Emissions']!=0)].reset_index(drop=True)
#print(heat_map.head())

# Calculate rank for each country for the FS Stage
heat_map['stage_wise_rank'] = heat_map.groupby(["Food System Stage",'GHG'])["GHG Emissions"].rank("dense", ascending=False)
heat_map['stage_wise_rank'] = heat_map['stage_wise_rank'].astype(int)
# Pivot to get the wide view where columns denote each stage and contain ranks by stage emission - higher the worse
heat_map_pivot = pd.pivot_table(heat_map, values='stage_wise_rank', index='Country', columns='Food System Stage')
# # Remove any na records
heat_map_pivot = heat_map_pivot.dropna()
heat_map_pivot['country'] = heat_map_pivot.index



countries = df1.Country.unique() 
line_chart = pd.melt(df1,
                    id_vars=["Industry","Scenario","Country","Emission"],
                    var_name="Year",
                    value_name="Emissions")
agg_view = line_chart.groupby(["Scenario","Country","Emission","Year"])["Emissions"].sum().reset_index()




edgar_sankey = food_df[(food_df["Year"]==2015)].groupby(by= ["GHG",
"Stage","Country"]).sum()[["GHG Emissions"]]

edgar_sankey = edgar_sankey.reset_index()


all_countries = edgar_sankey.Country.unique()



# Food emission ranking 
energy_emissions = df2.fillna(0)
current_emissions = energy_emissions.loc[energy_emissions['Scenario']=='Current Policy'].groupby(['Country'], as_index = False).agg({'2018':'sum'})
current_emissions['country'] = current_emissions['Country'].map(country_dict)
current_emissions = current_emissions.dropna()
current_emissions['energy_emission_ratings'] = np.where(current_emissions['2018']>10,'High',
                                               np.where(current_emissions['2018']>3,'Medium','Low'))

food_emissions_rankings = pd.merge(current_emissions[['country','energy_emission_ratings']],heat_map_pivot,on='country')

food_emissions_rankings.index = food_emissions_rankings['country'] + ', Energy Emission Level: ' + food_emissions_rankings['energy_emission_ratings']



fig = ff.create_annotated_heatmap(z = np.around(food_emissions_rankings.drop(['country','energy_emission_ratings'], axis=1).to_numpy(),0),
                                  y = food_emissions_rankings.drop(['country','energy_emission_ratings'], axis=1).index.tolist(),
                                  x = food_emissions_rankings.drop(['country','energy_emission_ratings'], axis=1).columns.tolist(),
                                  showscale=True,
                                  colorscale='RdYlGn',
                                font_colors=["black"],
                                hoverongaps=True)



# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


index_page = html.Div(style={'background-image':'url("/assets/Background4.jpg")',
  'width':'100%',
  'height':'35vh',
  'backgroundColor': colors['background']},
children=[
    html.Div(children=[
        html.H1(children='Enabling responsible production lines and green consumption links', style={'textAlign': 'left','color': colors['background'],"margin-left": "2rem",
        "margin-right": "2rem"
        }),
    
     html.Div(children='''Energy is the backbone of modern economy. Pollutant emissions from energy sector have been high globally due to the high dependence on energy for economic activity in the industrial world. This website intends to illustrate how sustainable development efforts will make impact in future through domino effect across industries
For illustration purposes, we use the energy sector as benchmark and bring out a view to help policymakers across countries design tax reforms to support sustainable developmental efforts. These choices will shape our energy use, our environment and our wellbeing through directed focus across sectors
       ''',style={'textAlign': 'left',
        'color': colors['background'],
        'fontSize': 18,
        "margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}),
        html.Div(className = 'row',children=[ html.H1("Select a Country",style={'textAlign': 'center','fontSize': 20}),
        dcc.Dropdown(id = 'country',
        options = [{'label':x ,'value':x} for x in sorted (df1.Country.unique())],
        placeholder="Select  Country",
        value = 'India',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        'width':'50%',
        'verticalAlign':"middle",
        "margin-left": "14rem",
        "margin-right": "2rem",
        "padding": "10px 10px",'display': 'inline-block'})])
       ,html.Div(className = 'row',children=[
        html.H1("Select a Pollutant",style={'textAlign': 'center','fontSize': 20}),
        dcc.Dropdown(id = 'emission',
        options = [{'label':x ,'value':x} for x in sorted (df1.Emission.unique())],
        placeholder="Select  Pollutant",
        value = 'PM',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        'width':'50%',
        "margin-left": "14rem",
        "margin-right": "2rem",
        "padding": "10px 10px",'display': 'inline-block'})]),

        html.Div(className = 'row',children=[dcc.Graph(
            id='graph1',
            figure = {},
            style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
         'width': '48%', 'display': 'inline-block'}
            
        ),dcc.Graph(
            id='graph3',
            figure = {},
            style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        'width': '48%', 'display': 'inline-block'}
            
        )])
                  
,
html.Div(children='''
        * Emissions of all air pollutants (SO2, NOX, PM2.5) are expressed in million tonnes (Mt) per year and are reported by sector
''',style={'textAlign': 'left',
        'color': colors['text1'],
        'fontSize': 12,
        "margin-left": "2rem",
        'padding':"0 0 10px 0"
        }),
        ### Line  chart
       html.Div(children='''
        These charts represent how the pollutant emissions from energy sector will project for future time periods, depending on policies adopted today. The three scenarios illustrated here are:
''',style={'textAlign': 'left',
        'color': colors['text1'],
        'fontSize': 18,
        "margin-left": "2rem",
        "margin-right": "2rem"
        }),

        html.Div(children='''    
       Current Policies Scenario:      
''',style={
        'color': colors['text1'],
        'fontSize': 18,"margin-left": "2rem",
        'font-weight': 'bold'}),
        html.Div(children='''
        The current policies which are adopted by individual country and have been in place are likely to make little or no impact towards containing energy emissions
''',style={
        'color': colors['text1'],"margin-left": "2rem",
        'fontSize': 18,"padding": "0 0 1em  0"}),
        html.Div(children='''
        Stated Policies Scenario: ''',style={
        'color': colors['text1'],"margin-left": "2rem",
        'fontSize': 18,'font-weight': 'bold'}),
        html.Div(children='''
        There are few nations that have ambitions announced by policy makers but have no clear anticipation on how these plans might change in future. Such actions will have transient impact which won't last long. Thus, their impact is limited''',style={
        'color': colors['text1'],"margin-left": "2rem",
        'fontSize': 18,"padding": "0 0 1em 0"}),
        html.Div(children='''
        Sustainable Development Scenario: ''',style={
        'color': colors['text1'],"margin-left": "2rem",
        'fontSize': 18,'font-weight': 'bold'}),
        html.Div(children='''
        There are three pillars to the Sustainable Development Scenario. These are to ensure universal energy access for all by 2030; to bring about sharp reductions in emissions of air pollutants; and to meet global climate goals in line with the Paris Agreement. These are likely to create the required big push to contain emissions so that we can try achieving a carbon neutral economic development''',style={
        'color': colors['text1'],"margin-left": "2rem",
        'fontSize': 18}),


        html.Br(),
        dcc.Link('Details on emissions from Food Processing', href='/Food-Industry',style={'textAlign':'centre',"margin-left": "24rem",'fontSize': 20}),
        html.Br(),
    html.Div(children="Clickable link for next page ",style={'textAlign':'centre',"margin-left": "24rem"}),
    ])
])
@app.callback(
    Output(component_id = 'graph1' ,component_property = 'figure' ),
    [Input(component_id = 'country',component_property = 'value')])

def update_sunburst(country):
    fig1 = px.sunburst(df1[df1["Country"] ==country], 
                  path=['Country', 'Emission','Industry'], 
                  values='2018',
                  hover_data=["Emission"],
                  title = f"Air pollutant emissions* for {country} in 2018")
    fig1.update_layout(paper_bgcolor=colors['background'])
    return fig1


@app.callback(
    Output(component_id = 'graph3' ,component_property = 'figure' ),
    [Input(component_id = 'country',component_property = 'value'),
    Input(component_id = 'emission',component_property = 'value')]
)

def update_line(country,emission):
    fig3 = px.line(line_chart[(line_chart.Year.isin(['2018','2025','2030','2040']))&
                          (line_chart["Country"]== country )&
                          (line_chart["Emission"]== emission)].
              groupby(["Year","Country","Emission","Scenario"]).
              agg({'Emissions':sum}).
              reset_index(), 
              
              x="Year", 
              y="Emissions", 
              color='Scenario',
              markers = True,
              labels={"Scenario": "Policy Scenarios"},
              title = f"Projected policy scenarios for {emission} in {country}")
    fig3.update_layout(paper_bgcolor=colors['background'])
    return fig3
    

page_1_layout = html.Div(
    style={'background-image':'url("/assets/Background4.jpg")',
  'width':'100%',
  'height':'50vh',
  'backgroundColor': colors['background']},children=[
    html.Div(children=[
        html.H1(children='Food Processing Industry', style={'textAlign': 'left','color': colors['background'],"margin-left": "2rem",
        "margin-right": "2rem"}),
       
        ### Sunburst chart 
        html.Div(children='''
        Food processing has deep backward and forward linkages. Due to the perishable nature of products, this industry has substantial organic waste that can be naturally recycled but due to the direct involvement in food chain, any contamination here is dangerous to entire human race.''',style={'textAlign': 'Left',
        'fontSize': 18,'color': colors['background'],"padding": "0 0 1em 0 ",
        "margin-right": "2rem","margin-left": "2rem"}),
        html.Br(),
        html.Div(children="GHG emissions from human activities are the main driver of climate change and food systems are a significant contributor with one third (~34%) of total global GHG emissions from human activities coming from food systems each year, based on multiple U.N.-backed studies released in 2021. via United Nations, FAO",
className="box1",
style={

'color':'white',
"margin-left": "2rem",
'height':'170px',
'width':'30%',
'text-align':'left',
'display':'inline-block',
}),

html.Div(children="The impacts of climate change such as increasing temperatures and changing precipitation patterns are already affecting the security of food systems and negative impacts are expected to increase based on future projected climate change, resulting in further declines of crop yields and increasingly higher food prices. via IPCC",className="box2",
style={

'color':'white',
'height':'170px',
'margin-left':'10px',
'width':'30%',
'text-align':'center',
'display':'inline-block',
}),

html.Div(children="As of May 2021, 70% of U.S. adults now favor taxing corporations based on their emissions, among other proposals aimed at reducing the effects of climate change that majorities of Americans support. via Pew Research Center",className="box2",
style={

'color':'white',
'height':'170px',
'margin-left':'10px',
'width':'30%',
'text-align':'right',
'display':'inline-block',
}),
        html.H1("Select a Country",style={'textAlign': 'center','fontSize': 20}),

        dcc.Dropdown(id = 'country1',
        options = [{'label':x ,'value':x} for x in sorted (food_sunburst.Country.unique())],
        placeholder="Select  Country",
        value = 'India',style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        'width':'50%',
        'verticalAlign':"middle",
        "margin-left": "14rem",
        "margin-right": "2rem",
        "padding": "10px 10px",'display': 'inline-block'}),

        html.Div(className = 'row',children=[dcc.Graph(
            id='graph_sun',
            figure = {},
            style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        'width': '48%', 'display': 'inline-block'}
            
        ),dcc.Graph(
            id='sankey-chart',
            figure = {},
            style={'textAlign': 'center',
        'color': colors['text1'],
        'fontSize': 20,
        'width': '48%', 'display': 'inline-block'})]),
html.Div(children='''
        * Emissions of all GHGs are expressed in metric tons CO2 equivalents
''',style={'textAlign': 'left',
        'color': colors['text1'],
        'fontSize': 12,
        "margin-left": "2rem",
        'padding':"0 0 10px 0"
        }),
        
    html.Div(children='''
        We have categorized the different stages of food processing industry in to production, consumption and waste creation activity zones. This zoning helps us understand how policy actions should be directed at a macro level and promote positive externality or reduce negative externality from these activities

''',style={'textAlign': 'left',
        'color': colors['text1'],
        'fontSize': 18,
        "margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}),
    dcc.Graph(figure=fig),
    html.Div(children='''
        Since, energy sector is the backbone of economic activity within a nation, we benchmarked our industrial analysis on the same. If a country is placed on lower side of the spectrum in energy emissions and has a high emission from certain stages of particular industry, food processing in current page, we will flag this as a risk to manage through corrective policy action(s).
Similarly, if there is a country that is placed on higher side of the spectrum in energy emissions and has a low emission from certain stages of particular industry, food processing in current page, we will flag this as an opprotunity to incentivize and learn from this stage. Potentially, a deep dive to the stage in history can give us answers to problems faced by other stages/industries/sectors/economies
''',style={'textAlign': 'left',
        'color': colors['text1'],
        'fontSize': 18,
        "margin-left": "2rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem"}),

    html.Div(id='page-1-content'),
    html.Br(),
    dcc.Link('Back to Energy Emissions view', href='/',style={'textAlign':'left',"margin-left": "24rem",'fontSize': 20}),
    
    ])
])
@app.callback(
    Output(component_id = 'graph_sun' ,component_property = 'figure' ),
    [Input(component_id = 'country1',component_property = 'value')])

def update_sunburst(country1):
    fig1 = px.sunburst(food_sunburst[food_sunburst["Country"]==country1],
            path=['Country', 'GHG','Food System Stage'],
            values='GHG Emissions',
            hover_data=["GHG"],
            title = f"Air pollutant emissions* for  {country1}")
    fig1.update_layout(paper_bgcolor=colors['background'])
    return fig1

@app.callback(
    Output("sankey-chart", "figure"), 
    [Input("country1", "value")])

def update_line_chart(country1):
    mask = edgar_sankey['Country'].isin([country1])
    
    fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    node = dict(
      pad = 20,
      thickness = 20,
      line = dict(color = "grey", width = 0.5),
      label = [
          "Carbon dioxide (CO2)", "Methane (CH4)", "Nitrous oxide (N2O)",
          "F-gases", "Production","Consumption","Waste"],
      color = ["#3d6493", "#95ceeb", "#308bbc", "#86aad1", "#58805b", 
               "#98c7a0", "#f36e3a", "#fba644", "#ad5849", "#d2c795", "#736a62", "#b0a08c"]),
      link = dict(
          source = [emission_gas[i] for i in list(edgar_sankey[mask].GHG.values)], # corresponds to 4 GHGs (the 'sources')
          target = [st[i] for i in list(edgar_sankey[mask]["Stage"].values)], # corresponds to 8 food system stages (the 'targets') 
          value  = list(edgar_sankey[mask]["GHG Emissions"].values) #the amount per Source to Target
      ))])

    fig.update_layout(
        title_text=f"Food System Emissions across different stages for {country1} in 2015"
        )
    return fig

    


@app.callback(dash.dependencies.Output('page-1-content', 'children'),
              [dash.dependencies.Input('page-1-dropdown', 'value')])
def page_1_dropdown(value):
    return 'You have selected "{}"'.format(value)



# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/Food-Industry':
        return page_1_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0', port=8050)
