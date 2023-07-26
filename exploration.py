import streamlit as st
import plotly.express as px
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
data = pd.read_excel('VN-BANK-CAMEL_0715.xls', sheet_name='Sheet1', header=0)
data.dropna(subset=['NPL', 'TOTAL_EQUITY', 'TOTAL_ASSETS',
       'TOTAL_LOANS', 'CASH', 'NET_INCOME'], inplace=True,axis=0,how='any')
data['OPERATING_EXP'] = data['NET_INCOME']*1.5
pctrank = lambda x: x.rank(pct=True)
# C là Capital: Equity/Asset
# A là Asset Quality: NPL/Asset (hoặc NPA/Asset)
# M là Management: Operatibg expenses/Asset (hoặc noninterest expenses/asser)
# E là Earning: Income/Asset hoặc ROA
# L là Liquidity: CAsh/asset
data['Capital']= data['TOTAL_EQUITY']/data['TOTAL_ASSETS']
data['Asset Quality']= data['NPL']/data['TOTAL_ASSETS']
data['Management'] = data['OPERATING_EXP']/data['TOTAL_ASSETS']
data['Earning'] = data['NET_INCOME']/data['TOTAL_ASSETS']
data['Liquidity'] = data['CASH']/data['TOTAL_ASSETS']
ratios = ['Capital','Asset Quality','Management','Earning','Liquidity']
figures =['NPL', 'TOTAL_EQUITY', 'TOTAL_ASSETS','TOTAL_LOANS', 'CASH', 'NET_INCOME','OPERATING_EXP']
data.sort_values(by=['Bank', 'Year'], inplace=True)


def color_ratio(val):
    color = '#F21D2F' if val<0.08 else '#F2AC29' if val<0.09 else '#14A653'
    return f'background-color: {color}'

data.sort_values(by='TOTAL_ASSETS',ascending=False,inplace=True)

# def calculation(data):
#     data['CAPITAL']= data['TOTAL_EQUITY']/[data['TOTAL_ASSETS']
#     data['ASSET_QUALITY']= data['NLP']/data['TOTAL_ASSETS']
#     # data['MANAGEMENT'] = data['NET_INCOME']/data['TOTAL_ASSETS']
#     data['EARNING'] = data['NET_INCOME']/data['TOTAL_ASSETS']


# Cap < 0.08 --> red; Cap >=0.08;<=0.09 --> yellow; Cap > 0.09 --> green
data[data.Year==2022].Bank.value_counts()

tab1, tab2= st.tabs(["Yearly details","Ratio View"])

year_select = tab1.selectbox('Select year', data.Year.unique())
tab1_df =data.loc[data.Year==year_select,['Bank','Capital','Asset Quality','Management','Earning','Liquidity']]

tab1.dataframe(tab1_df.set_index('Bank').round(4).style.format('{:.2%}').applymap(color_ratio,subset=['Capital','Asset Quality','Management','Earning','Liquidity']))
tab1.header(f'Year {year_select} warning list')
tab1.subheader('Ratio under 8%')
ratio_tabs = tab1.tabs(ratios)
for ratio,ratio_tab in zip(ratios,ratio_tabs):
        ratio_tab.dataframe(data[(data.Year==year_select)&(data[ratio]<0.08)]\
                            .drop(columns=['Year','ID','Industry']).set_index('Bank').round(4)\
                            .style.format({col:"{:.2%}" for col in ratios}|{c:"{:,.0f}" for c in figures})\
                            .applymap(color_ratio,subset=ratios))


# tab1.dataframe(data[(data.Year==year_select)&(data['Capital']<0.08)].drop(columns=['Year','ID','Industry']),hide_index=True)

tab1.subheader('Continuos declining Caps')
# 3 years declining in a row
for _ in ratios:
    data[_+'_pct_change']=data.groupby('Bank')[_].pct_change()
tab1.dataframe(data[data.Bank.isin(data[data.Year==year_select].Bank.unique())].sort_values(by=['Bank','Year']))



ratio = tab2.selectbox('Select ratio', ratios)
tab2.markdown(f'### {ratio} Heatmap')

#heatmap    
fig = px.imshow(data.pivot_table(index='Bank', columns='Year', values=ratio, aggfunc='sum').round(decimals=2),
                text_auto=True,
                aspect='auto',
                zmin=0,         # Minimum value for the color scale
                zmax=1,
                color_continuous_scale=[[0.0, '#F21D2F'], [0.08, '#F21D2F'], [0.08, '#F2AC29'], [0.09, '#F2AC29'],[0.09, '#14A653'],[1, '#14A653']],
                )
fig.update_layout(
    height=800,   # Adjust the height to make sure all text and axes are clear
    width=800,    # Adjust the width to make sure all text and axes are clear
    font=dict(size=22   ),  # Decrease the font size for the tick labels
    legend=dict(font=dict(size=6)),  # Decrease the font size for the legend

)  # Increase the font size for clearer text on the heatmap

# Show all values on the axes
fig.update_xaxes(tickvals=list(range(len(data['Year'].unique()))), ticktext=list(data['Year'].unique()))
fig.update_yaxes(tickvals=list(range(len(data['Bank'].unique()))), ticktext=list(data['Bank'].unique()))
fig.update_coloraxes(colorbar=dict(tickfont=dict(size=10)))
fig.update_coloraxes(colorbar_tickmode='array',colorbar_tickvals=[4,8.5,50],colorbar_ticktext=['<8%','8%-9%','>9%'])


tab2.plotly_chart(fig)



