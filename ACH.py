#python-test % python3 -m streamlit run Carlos_App/ach_report_2.py 

#input example SubMerchantIBFundingReject_315300_20230925

#we can add these fields to the query
#Partner Source		
#Stax Merchant ID
#hubspot ticket
#ticket created date

import streamlit as st
import pandas as pd
import numpy as np
import io
import datetime
import xlsxwriter
from datetime import date, timedelta

st.title("Stax ACH Report Builder")

st.write("ACH Rejects MODE CSV Download  [link](https://app.mode.com/editor/fattmerchant/reports/666e0d6be67c/queries/97c542996f64)")

image = open('mode_instructions.png', 'rb').read()
st.image(image, caption='For 8 digit MID add a 0, otherwise post mids in this section with single quote and comma format', use_column_width=True)

engine_df = st.file_uploader("Upload ACH Rejects MODE CSV Download CSV file", type=['csv'], key='StaxEngine')

uploaded_files = st.file_uploader("Upload ACH REJECT CSV", type="csv", accept_multiple_files=True)

if engine_df is not None and uploaded_files:
    for file in uploaded_files:
        file.seek(0)
    uploaded_data_read = [pd.read_csv(file) for file in uploaded_files]

    dfpreclean = pd.concat(uploaded_data_read)

    engine_df = pd.read_csv(engine_df)

    buffer = io.BytesIO()

    dfpreclean2 = dfpreclean.loc[:,['Return Date', 'Original Date', 'Attempted Funds Transfer Date',
       'Sub Merchant Business Name', 'Funding Sub Merchant ID', 'Funds Transfer Request ID', 
       'Funds Transfer Amount', 'Reason Code', 'Reason Message',
       ]]
    
    dda = dfpreclean.loc[:,['Routing Number', 'Account Number', 'Account Name']]

    dfpreclean2['Funds Transfer Amount'] = dfpreclean2['Funds Transfer Amount'] / 100.00

    dfpreclean2['Funding Sub Merchant ID'] = dfpreclean2['Funding Sub Merchant ID'].apply(str)
    dfpreclean2['Funding Sub Merchant ID'] = dfpreclean2['Funding Sub Merchant ID'].apply(lambda x: '0' + x  if len(x) == 8 else x)

    engine_df['processor_merchant_id'] = engine_df['processor_merchant_id'].apply(str)
    engine_df['processor_merchant_id'] = engine_df['processor_merchant_id'].apply(lambda x: '0' + x  if len(x) == 8 else x)

    dfpreclean3 = dfpreclean2[dfpreclean2['Sub Merchant Business Name'] != 'Fattmerchant Platform Account']

    merged_df = pd.merge(dfpreclean3, engine_df, left_on='Funding Sub Merchant ID', right_on='processor_merchant_id', how='left')


    #dfpreclean3['Partner Source'] = ''
    merged_df['Settlement ID'] = ''
    merged_df['Add. Notes'] = ''
    merged_df['New Ticket?'] = ''

    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
      #  dfpreclean3.to_excel(writer, sheet_name='Clean_Data', index=False)
        merged_df.to_excel(writer, sheet_name='Clean_Data', index=False)
        dda.to_excel(writer, sheet_name='dda', index=False)

        # Close the Pandas Excel writer and output the Excel file to the buffer
        writer.close()

        st.download_button(
            label="Download Excel worksheets",
            data=buffer,
            file_name="achrejects.xlsx",
            mime="application/vnd.ms-excel"
        )

else:
   st.warning("you need to upload a csv file.")














