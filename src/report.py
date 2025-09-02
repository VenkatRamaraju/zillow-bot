#!/usr/bin/env python3

import pandas as pd

def generate_report(properties):    
    # convert to dataframe
    df = pd.DataFrame(properties)
    df.rename(columns={
        'daysOnZillow': 'days_on_zillow',
        'livingArea': 'sqft'
    }, inplace=True)

    # order columns
    priority_columns = ['address', 'price', 'zestimate', 'bedrooms', 'bathrooms', 'days_on_zillow', 'sqft']
    remaining_columns = [col for col in df.columns if col not in priority_columns]
    ordered_columns = priority_columns + remaining_columns
    df = df[ordered_columns]
    
    return df