import streamlit as st
import base64
import requests
import datetime
import pandas as pd
import re
import os
import numpy as np
from pandas.tseries.offsets import BDay
from datetime import timedelta, date

# Function to determine new file name based on initial name
def determine_new_name(file_name):
    if file_name.startswith('finance_1'):
        return 'sales.csv'
    elif file_name.startswith('job_list1'):
        return 'output_file.csv'
    else:
        return file_name  # or some default logic
    

def get_state_variable(var_name, default_value):
    if 'st_state' not in st.session_state:
        st.session_state['st_state'] = {}
    if var_name not in st.session_state['st_state']:
        st.session_state['st_state'][var_name] = default_value
    return st.session_state['st_state'][var_name]

# Initialize session state for authentication
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False


# Branch Mapping Dictionary
branch_mapping = {
    'Halo (Bognor Regis)': 'Bognor (A)',
    'Halo (Poole)': 'Poole (B)',
    'Halo (Westbury)': 'Westbury (C)',
    'Halo (Cardiff)': 'Cardiff (E)',
    'Halo (Crewe)': 'Crewe (F)',
    'Halo (Eastleigh)': 'Eastleigh (H)',
    'Halo (Portsmouth)': 'Portsmouth (N)',
    'Halo (Eastbourne)': 'Eastbourne (P)',
    'Halo (Amesbury)': 'Amesbury (R)',
    'Halo (Chandlers Ford)': 'Chandlers (I)',
    'Halo (Basingstoke)': 'Basingstoke (J)',
    'Halo (Bristol)': 'Bristol (K)',
    'Halo (Cheltenham)': 'Cheltenham (L)',
    'Halo (Bournemouth)': 'Bournemouth (M)',
    'Halo (Innovation Centre)': 'Innovation (A)',
    'Halo (Stoke-On-Trent)': 'Stoke (O)',
    'Halo (Shoreham)': 'Shoreham (Q)',
    'Halo (Trafford)': 'Trafford (S)',
    'Halo (Swindon)': 'Swindon (T)',
    'Halo (Lincoln)': 'Lincoln (U)',
    'Halo (Wakefield)': 'Wakefield (V)',
    'Halo (Guildford)': 'Guildford (W)',
    'Halo (York)': 'York (X)',
    'Halo (Harrow)': 'Harrow (Y)',
    'Halo (West Thurrock)': 'West Thurrock (Z)'
}
    # Define branch order for sorting
branch_order = [
    'Bognor (A)', 'Poole (B)', 'Westbury (C)', 'Cardiff (E)', 'Crewe (F)',
    'Eastleigh (H)', 'Portsmouth (N)', 'Eastbourne (P)', 'Amesbury (R)',
    'Chandlers (I)', 'Basingstoke (J)', 'Bristol (K)', 'Cheltenham (L)',
    'Bournemouth (M)', 'Innovation (A)', 'Stoke (O)', 'Shoreham (Q)',
    'Trafford (S)', 'Swindon (T)', 'Lincoln (U)', 'Wakefield (V)',
    'Guildford (W)', 'York (X)', 'Harrow (Y)', 'West Thurrock (Z)'
]




def process_data(uploaded_file, new_file_name):

    if new_file_name == 'output_file.csv':
        # Read the .csv file into a DataFrame
        df = pd.read_csv(uploaded_file, skiprows=2)

        # Remove all empty rows
        df.dropna(how='all', inplace=True)

        # Remove rows where the first cell doesn't start with a letter followed by a number
        df = df[df[df.columns[0]].apply(lambda x: re.match(r'^[A-Za-z][0-9]', str(x)) is not None)]
        
        # Exclude rows with "HWARR" or "HALO" in the "Debtor" column
        df = df[~df["Insurer"].str.contains("HWARR|HALO|Unknown|BLOCK|OTHER", case=False, na=False)]
        df = df[~df["Source Code"].str.match("HALO Warranty", case=False, na=False)]
        df = df[~df["Write Off Date/Time"].str.contains("/", case=False, na=False)]
        df = df[~df["Job Status"].astype(str).str.contains("Closed|HALO|Cancelled", case=False, na=False)]
        df = df[df["Reason"].isna()]
        #st.write(df.head())

        # Convert branch names using the mapping
        df['Location'] = df['Location'].map(branch_mapping)

        # Reset index for cleaner output
        df.reset_index(drop=True, inplace=True)








        

                # Specify the datetime format used in your Excel file
        current_date = datetime.datetime.now().date()
        # Assuming df is your DataFrame
        extracted_data = df[['Job Number', 'Location', 'Vehicle Registration', 'Insurer', 'Arrived On Site Date/Time', 'Left Site Date/Time', 'OnSite-WSComp', 'Arrival', 'WS Completed Date/Time']].copy()

        # Converting date/time columns to datetime format
        date_time_columns = ['Arrived On Site Date/Time', 'Left Site Date/Time', 'WS Completed Date/Time']
        datetime_format = "%d/%m/%Y %H:%M"

        for col in date_time_columns:
            if col in extracted_data.columns:
                extracted_data.loc[:, col] = pd.to_datetime(extracted_data[col], format=datetime_format, errors='coerce')

        # Your existing calculations
        extracted_data['Key to Key'] = (extracted_data['Left Site Date/Time'] - extracted_data['Arrived On Site Date/Time']).apply(lambda x: x.days + (x.seconds / 86400) if pd.notnull(x) else None).astype(float)
        df['Key to Key'] = extracted_data['Key to Key']

        # Save the cleaned DataFrame to a new .csv file

        df.to_csv(uploaded_file, index=False)

        #st.write(df.head())

        return uploaded_file









def display_page():

    st.title('Halo Dashboard - Upload BMS Reports')

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    
    if uploaded_file is not None:
        # Determine the new file name

        new_file_name = determine_new_name(uploaded_file.name)

        cleaned_file = process_data(uploaded_file, new_file_name)



        # Check if cleaned_file is not None and is a file-like object
        if cleaned_file and hasattr(cleaned_file, 'read'):
            # Reset the file pointer to the start of file-like object
            cleaned_file.seek(0)

            # Read the contents of the file
            file_content = cleaned_file.read()

            # Check if file_content is not empty
            if file_content:
                # Encode the content to base64
                content = base64.b64encode(file_content).decode("utf-8")
                #st.write(content)
            else:
                st.error("The processed file is empty.")
        else:
            st.error("No valid processed file to encode.")

        #st.write(content)









        # GitHub API URL
        url = f"https://api.github.com/repos/tdambrowitz/audio_minutes/contents/{new_file_name}"

        headers = {
            "Authorization": "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"  # Replace with your actual token
        }

        # Check if the file exists to get its SHA (necessary for updating files)
        existing_file_response = requests.get(url, headers=headers)

        st.write(existing_file_response.status_code)

        if existing_file_response.status_code == 200:
            sha = existing_file_response.json().get('sha')
        else:
            sha = None

        st.write(new_file_name)

        # Prepare the request payload for updating the file
        payload = {
            "message": f"Upload CSV as {new_file_name}",
            "committer": {
                "name": "Your Name",
                "email": "your_email@example.com"
            },
            "content": content
        }

        # Include SHA if updating an existing file
        if sha:
            payload["sha"] = sha

        # Send the request
        response = requests.put(url, json=payload, headers=headers)

        #st.write(response.text)

        if response.status_code in [200, 201]:
            st.success('File uploaded to GitHub successfully!')
        else:
            st.error(f'Failed to upload file: {response.content.decode("utf-8")}')



































    # Calculate the date of the next Friday
    today = datetime.date.today()
    days_until_friday = (4 - today.weekday()) % 7  # Calculate days until next Friday
    next_friday = today + datetime.timedelta(days=days_until_friday)

    # Add one week to the next Friday's date
    next_friday_plus_one_week = next_friday + datetime.timedelta(weeks=2)

    # Type the date of the next work week
    due_in_date = next_friday_plus_one_week.strftime('%d/%m/%Y')
    

    # Find the previous workday
    if today.weekday() == 0:  # Monday
        previous_workday = today - datetime.timedelta(days=3)
    else:
        previous_workday = today - datetime.timedelta(days=1)

    # Type the date of the previous workday
    yesterday = previous_workday.strftime('%d/%m/%Y')



    with st.expander("How do I run the Due In report?"):
        st.write('1. Navigate to the "Vehicles Due In" report (found under "Administration" in BMS)')
        st.write('2. Set the "Location" selector to "All Branches"')
        st.write('3. Set the "Report Output Format" selector to "Open With Excel"')
        st.write(f'4. Set the "Due On Site Or Before" selector to {due_in_date}')
        st.write('5. Click "Print" then close the excel file that opens (save it somewhere if you want, or navigate to the RUNCLIENT folder.)')
        st.write('6. Come back to this page and upload the file (it should start with "vehicle_due_in" and end with ".csv")')

    with st.expander("How do I run the On-Site report?"):
        st.write('1. Navigate to the "Vehicles On Site" report (found under "Administration" in BMS)')
        st.write('2. Set the "Location" selector to "All Branches"')
        st.write('3. Set the "Report Output Format" selector to "Open With Excel"')
        st.write('4. Click "Print" then close the excel file that opens (save it somewhere if you want, or navigate to the RUNCLIENT folder.)')
        st.write('5. Come back to this page and upload the file (it should start with "vonsite_" and end with ".csv")')

    with st.expander("How do I run the Arrived Yesterday report?"):
        st.write('1. Navigate to the "Job Listing" report (found under "Job Analysis" in BMS)')
        st.write('2. Set the "Date" selector to "Onsite"')
        st.write(f'3. Set the "From Date" and "To Date" selectors to {yesterday}')
        st.write('4. Click "Print" then close the excel file that opens (save it somewhere if you want, or navigate to the RUNCLIENT folder.)')
        st.write('5. Come back to this page and upload the file (it should start with "job_list1_" and end with ".csv")')

        
        


# Logic for password checking
def check_password():
    if not st.session_state.is_authenticated:
        password = st.text_input("Enter Password:", type="password")


            
        
        if password == "Halo2023*":
            st.session_state.is_authenticated = True
            st.rerun()
        elif password:
            st.write("Please enter the correct password to proceed.")
            
        blank, col_img, col_title = st.columns([2, 1, 3])

        # Upload the image to the left-most column
        with col_img:
            st.image("https://s3-eu-west-1.amazonaws.com/tpd/logos/5a95521f54e2c70001f926b8/0x0.png")


        # Determine the page selection using the selectbox in the right column
        with col_title:
            #st.title("Created By Halo")
            st.write("")
            st.markdown('<div style="text-align: left; font-size: 40px; font-weight: normal;">Created By Halo*</div>', unsafe_allow_html=True)
            
        blank2, col_img2, col_title2 = st.columns([2, 1, 3])

        # Upload the image to the left-most column
        with col_img2:
            st.image("https://th.bing.com/th/id/OIP.42nU_MRx_INTLq_ejdHxBQHaCe?pid=ImgDet&rs=1")


        # Determine the page selection using the selectbox in the right column
        with col_title2:
            
            #st.title("Powered By IRS")
            st.markdown('<div style="text-align: left; font-size: 30px; font-weight: normal;">Powered By IRS</div>', unsafe_allow_html=True)
        # Fill up space to push the text to the bottom
        for _ in range(20):  # Adjust the range as needed
            st.write("")

        # Write your text at the bottom left corner
        st.markdown('<div style="text-align: right; font-size: 10px; font-weight: normal;">* Trenton Dambrowitz, Special Projects Manager, is "Halo" in this case.</div>', unsafe_allow_html=True)



    else:
        print("Access granted, welcome to the app.")
        display_page()


check_password()