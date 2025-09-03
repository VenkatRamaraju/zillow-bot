#!/usr/bin/env python3

# imports
import json
import pandas as pd
from typing import List
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import StringIO

# load config
with open('config.json', 'r') as f:
    config = json.load(f)

def send_email(report: pd.DataFrame, new_properties_df: pd.DataFrame, email_list: List[str]):
    subject = "Weekly Zillow Properties Report"
    
    # create body based on whether we have new properties
    if new_properties_df is not None and not new_properties_df.empty:
        body = f"Hi,\n\nPlease find attached the latest properties report from your Zillow search.\n\nThis week we found {len(new_properties_df)} new properties, which are included in a separate attachment (new_properties.csv).\n\nBest regards,\nZillow Bot"
    else:
        body = "Hi,\n\nPlease find attached the latest properties report from your Zillow search.\n\nNo new properties were found this week compared to last week.\n\nBest regards,\nZillow Bot"

    # get email config
    email_config = config.get('email_config', {})
    smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
    smtp_port = email_config.get('smtp_port', 587)
    
    # get sender credentials from environment variables or config
    sender_email = email_config.get('sender_email', '')
    sender_password = email_config.get('sender_password', '')
    
    if not sender_email or not sender_password:
        print("error: sender email and password must be set in environment variables or config")
        return
    
    # convert dataframe to csv string
    csv_buffer = StringIO()
    report.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    # convert new properties dataframe to csv string if it exists
    new_properties_csv_data = None
    if new_properties_df is not None and not new_properties_df.empty:
        new_properties_csv_buffer = StringIO()
        new_properties_df.to_csv(new_properties_csv_buffer, index=False)
        new_properties_csv_data = new_properties_csv_buffer.getvalue()
    
    # send individual emails
    try:
        # create smtp connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # enable security
        server.login(sender_email, sender_password)
        
        for recipient_email in email_list:
            # create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject if subject else "zillow properties report"
            
            # add body
            email_body = body if body else "please find attached the latest properties report."
            msg.attach(MIMEText(email_body, 'plain'))
            
            # create csv attachment for main report
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(csv_data.encode('utf-8'))
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment; filename="properties_report.csv"')
            msg.attach(attachment)
            
            # create csv attachment for new properties if it exists
            if new_properties_csv_data is not None:
                new_properties_attachment = MIMEBase('application', 'octet-stream')
                new_properties_attachment.set_payload(new_properties_csv_data.encode('utf-8'))
                encoders.encode_base64(new_properties_attachment)
                new_properties_attachment.add_header('Content-Disposition', 'attachment; filename="new_properties.csv"')
                msg.attach(new_properties_attachment)
            
            # send email
            text = msg.as_string()
            server.sendmail(sender_email, recipient_email, text)
            print(f"email sent successfully to {recipient_email}")
        
        server.quit()
        print(f"all emails sent successfully to {len(email_list)} recipients")
        
    except Exception as e:
        print(f"error sending email: {str(e)}")
        print("make sure sender credentials are correct and less secure app access is enabled for gmail")
