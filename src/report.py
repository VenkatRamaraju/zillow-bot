#!/usr/bin/env python3

import pandas as pd
import boto3
import json
import os
from datetime import datetime, timedelta

# load config
with open('config.json', 'r') as f:
    config = json.load(f)

# create s3 client with credentials
s3 = boto3.client(
    's3',
    aws_access_key_id=config['aws_config']['access_key'],
    aws_secret_access_key=config['aws_config']['secret_key'],
    region_name=config['aws_config']['region']
)

def upload_to_s3(df):
    # file name is the current week
    week = datetime.now().strftime('%Y-%W')
    file_name = f'zillow_report_{week}.csv'
    
    # save dataframe to temp csv file with explicit utf-8 encoding
    temp_file_path = f'/tmp/{file_name}'
    df.to_csv(temp_file_path, index=False, encoding='utf-8')
    
    # upload to s3
    s3.upload_file(temp_file_path, config['aws_config']['bucket_name'], file_name)
    
    # clean up temp file
    os.remove(temp_file_path)

def read_previous_week_from_s3():
    # calculate previous week
    previous_week = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%W')
    previous_week_file_name = f'zillow_report_{previous_week}.csv'
    temp_file_path = f'/tmp/{previous_week_file_name}'

    try:
        # read from s3
        s3.download_file(config['aws_config']['bucket_name'], previous_week_file_name, temp_file_path)
        previous_week_df = pd.read_csv(temp_file_path, encoding='utf-8')

        # clean up file
        os.remove(temp_file_path)

        return previous_week_df
    except Exception as e:
        print(f"Could not read previous week's report: {e}")
        return None


def get_new_properties(current_week_df, previous_week_df):    
    # find addresses that are in current week but not in previous week
    previous_addresses = set(previous_week_df['address'])
    new_properties_mask = ~current_week_df['address'].isin(previous_addresses)
    new_properties_df = current_week_df[new_properties_mask].copy()
    return new_properties_df


def generate_report(properties):    
    # convert to dataframe
    df = pd.DataFrame(properties)
    df = df.sort_values('daysOnZillow', ascending=True)
    df.rename(columns={
        'daysOnZillow': 'days_on_zillow',
        'livingArea': 'sqft'
    }, inplace=True)

    # order columns
    priority_columns = ['address', 'price', 'zestimate', 'bedrooms', 'bathrooms', 'days_on_zillow', 'sqft']
    remaining_columns = [col for col in df.columns if col not in priority_columns]
    ordered_columns = priority_columns + remaining_columns
    df = df[ordered_columns]
    
    # get previous week data and identify new properties
    previous_week_df = read_previous_week_from_s3()
    if previous_week_df is not None:
        new_properties_df = get_new_properties(df, previous_week_df)
    else:
        new_properties_df = None
    
    return df, new_properties_df