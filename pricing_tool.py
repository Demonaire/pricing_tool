import pandas as pd
import numpy as np
from tabulate import tabulate


#extract SKU number out of asin
def extract_sku(asin):
    
    lst=asin.split('|')
    index=lst.index(stone)+2
    
    return lst[index]

#round price to nearest .99$
def round_99(price):
    
    try:
        price=round(price+0.01)-0.01
        return price
    
    except:
        return np.nan

#replace all stones in ENG file with clear to generate complete list of all possible SKUS
def make_all_clear(string):
    
    lst=string.split('|')
    lst[1]='Clear'
    string='|'.join(lst)
    return string

stone_prices=pd.read_excel('batch_stone_pricing.xlsx',sheet_name="Stone Price")
batch_price=pd.read_excel('batch_stone_pricing.xlsx',sheet_name="Batches")
company_price=pd.read_excel('batch_stone_pricing.xlsx',sheet_name="Company charges")

style_price=pd.read_excel('inventory file2.xlsx')
style_price=style_price[['New SKUS.1', '18k.1', '14k.1','Unnamed: 24']]
style_price=style_price.drop(index=0)
style_price=style_price.reset_index().drop(labels='index',axis=1)
style_price.columns=['New SKUS', '18k', '14k','Stone Weight']
style_price['SKU Number']=style_price['New SKUS'].apply(lambda x: x.split('/')[-1])

styles_dict={'1':'18k','2':'14k'}
stones=stone_prices['Rocks'].to_list()
company_dict={'1':'Amazon','2':'Ebay'}

#Take company input from user
while True:
    
    print('Please select relevant option for company for pricing ')
    print ("{:<8} {:<15}".format('Option','Company'))
    
    for key,value in company_dict.items():
        print("{:<8} {:<15}".format(key, value))
    option=input()
    
    try:

        company=company_dict[option]
        print('')
        print(f'Selected Company: {company}')
        company_multiplier=company_price[company_price['Company']==company]['Multiplier'].sum()
        company_overhead=company_price[company_price['Company']==company]['Company Overhead'].sum()
        break
    
    except:
        print('')
        print('Invalid option,please select again!')
        print('')
        continue

#Take engraving input from user

print('Please select 1 for engraving, anything else for non-engraving pricing ')

option=input()

if option=='1':

    engraving=True
    print( f'Engraving selected') 
else:

    engraving=False
    print('Engraving not selected') 


#take Metal style input from user
while True:
    
    print('Please select relevant option for metal style for pricing ')
    print ("{:<8} {:<15}".format('Option','Metal Style'))
    
    for key,value in styles_dict.items():
        print("{:<8} {:<15}".format(key, value))
    option=input()
    
    try:

        style=styles_dict[option]
        print('')
        print(f'Selected metal style: {style}') 
        break
    
    except:
        print('')
        print('Invalid option,please select again!')
        print('')
        continue

#Take stone input from user

while True:
    
    print('Please select relevant option for required stone for pricing ')
    print(tabulate(stone_prices[['Rocks']], headers=['Option','Stone'], tablefmt='psql'))
    
    option=input()
    
    try:

        stone=stone_prices.iloc[int(option),0]
        stone_price=stone_prices.iloc[int(option),1]
        print('')
        print(f'Selected stone: {stone}') 
        break
    
    except:
        print('')
        print('Invalid option,please select again!')
        print('')
        continue

if engraving==False:
    normal_df=pd.read_excel('14k clear stones.xlsx')
    normal_df=normal_df[['New Asin']]
    normal_df['Batch']=normal_df["New Asin"].apply(lambda x:x.split("|")[1][0:2])
    normal_df['Price']=np.nan
    normal_df['New Asin']=normal_df['New Asin'].apply(lambda x:x.replace('Clear',stone))
    normal_df['SKU Number']=normal_df['New Asin'].apply(extract_sku)
    
    #import style price & stone weight

    if style=='18k':
        normal_df=pd.merge(normal_df,style_price[['SKU Number','18k','Stone Weight']],on='SKU Number',how='left')
        normal_df.rename(columns={'18k': 'Style Price'}, inplace=True)
    else:
        normal_df=pd.merge(normal_df,style_price[['SKU Number','14k','Stone Weight']],on='SKU Number',how='left')
        normal_df.rename(columns={'14k': 'Style Price'}, inplace=True)
        
    #import stone price
    normal_df['Stone Price']=stone_price
        
    #import company multiplier & overhead
    normal_df['Company Multiplier']=company_multiplier
    normal_df['Company Overhead']=company_overhead
    
    #Batch price increment import
    normal_df=pd.merge(normal_df,batch_price,on='Batch',how='left')
    normal_df['Batch %age']=normal_df['Batch %age']+1
    
    #Calculate Final Price & round it to nearest .99$
    normal_df['Price']=(((normal_df['Style Price']+normal_df['Stone Weight']*normal_df['Stone Price'])*normal_df['Company Multiplier'])+normal_df['Company Overhead'])*normal_df['Batch %age']
    normal_df['Price']=normal_df['Price'].apply(round_99)
    
    #export Final Output
    normal_df=normal_df.replace(to_replace=np.nan,value="#N/A")
    normal_df=normal_df[['New Asin','Price']]
    normal_df.columns=['SKU','Price']
    normal_df.to_excel(f'{style} {stone} {company} noENG.xlsx',index=False)
    
    
else:
    
    normal_df=pd.read_excel('14k ENG.xlsx')
    normal_df=normal_df[['NEW SKU']]
    normal_df['NEW SKU']=normal_df['NEW SKU'].apply(make_all_clear)
    normal_df=normal_df.drop_duplicates()
    normal_df['Batch']=normal_df["NEW SKU"].apply(lambda x:x.split("|")[2][0:2])
    normal_df['Price']=np.nan
    
    normal_df['NEW SKU']=normal_df['NEW SKU'].apply(lambda x:x.replace('Clear',stone))
    normal_df['SKU Number']=normal_df['NEW SKU'].apply(extract_sku)
    
    #import style price & stone weight

    if style=='18k':
        normal_df=pd.merge(normal_df,style_price[['SKU Number','18k','Stone Weight']],on='SKU Number',how='left')
        normal_df.rename(columns={'18k': 'Style Price'}, inplace=True)
    else:
        normal_df=pd.merge(normal_df,style_price[['SKU Number','14k','Stone Weight']],on='SKU Number',how='left')
        normal_df.rename(columns={'14k': 'Style Price'}, inplace=True)
        
    #import stone price
    normal_df['Stone Price']=stone_price
        
    #import company multiplier & overhead
    normal_df['Company Multiplier']=company_multiplier
    normal_df['Company Overhead']=company_overhead
    
    #Batch price increment import
    normal_df=pd.merge(normal_df,batch_price,on='Batch',how='left')
    normal_df['Batch %age']=normal_df['Batch %age']+1
    
    #Calculate Final Price & round it to nearest .99$
    normal_df['Price']=((((normal_df['Style Price']+normal_df['Stone Weight']*normal_df['Stone Price'])*normal_df['Company Multiplier'])+normal_df['Company Overhead'])+30)*normal_df['Batch %age']
    normal_df['Price']=normal_df['Price'].apply(round_99)
    
    #export Final Output
    normal_df=normal_df.replace(to_replace=np.nan,value="#N/A")
    normal_df=normal_df[['NEW SKU','Price']]
    normal_df.columns=['SKU','Price']
    normal_df.to_excel(f'{style} {stone} {company} ENG.xlsx',index=False)