import pandas as pd
import streamlit as st
import re
from io import BytesIO
from datetime import datetime, timedelta, date
from github import Github, InputFileContent
import base64

# Include your token in an environment variable for safety
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]



def to_csv_bytes(df):
    output = BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()


def push_to_github(file_content, file_name, repo_name, branch_name="main"):
    st.write("Pushing to GitHub...")
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)

    # Encoding file content to Base64
    encoded_content = base64.b64encode(file_content).decode()
    st.write("File encoded")

    commit_message = f"Add processed data"
    path = f"{file_name}"  # Adjust path as needed
    st.write("Getting contents...")

    try:
        contents = repo.get_contents(path, ref=branch_name)
        repo.update_file(path, commit_message, encoded_content, contents.sha, branch=branch_name)
        st.write(f"File {file_name} updated in {repo_name} on branch {branch_name}")
    except Exception as e:
        repo.create_file(path, commit_message, encoded_content, branch=branch_name)
        st.write(f"File {file_name} created in {repo_name} on branch {branch_name}, exception encountered: " + str(e))





# Function to process data
def process_data(uploaded_file):
    df = pd.read_csv(
        uploaded_file,
        skiprows=2,
        usecols=range(69),  # Adjust range according to the structure of your CSV file.
        nrows=6000,
    )







    
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


    # Reset index for cleaner output
    df.reset_index(drop=True, inplace=True)

        

            # Specify the datetime format used in your Excel file
    current_date = datetime.now().date()
    # Assuming df is your DataFrame
    extracted_data = df[['Job Number', 'Location', 'Vehicle Registration', 'Insurer', 'Arrived On Site Date/Time', 'Left Site Date/Time', 'OnSite-WSComp', 'Arrival', 'WS Completed Date/Time']].copy()

    # Copy 'Left Site Date/Time' from df before conversion
    left_site_original = df['Left Site Date/Time'].copy()

    # Converting date/time columns to datetime format
    date_time_columns = ['Arrived On Site Date/Time', 'Left Site Date/Time', 'WS Completed Date/Time']
    datetime_format = "%d/%m/%Y %H:%M"

    for col in date_time_columns:
        if col in extracted_data.columns:
            extracted_data.loc[:, col] = pd.to_datetime(extracted_data[col], format=datetime_format, errors='coerce')

    # Your existing calculations
    extracted_data['Key to Key'] = (extracted_data['Left Site Date/Time'] - extracted_data['Arrived On Site Date/Time']).apply(lambda x: x.days + (x.seconds / 86400) if pd.notnull(x) else None).astype(float)
    df['Key to Key'] = extracted_data['Key to Key']



        # Convert 'Left Site Date/Time' to datetime and then extract just the date part
    left_site_original = pd.to_datetime(left_site_original, dayfirst=True).dt.date

    # Repopulate the 'Left Site Date/Time' column in df with original values
    df['Left Site Date/Time'] = left_site_original

    return df


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()  # This will save the content to the `output`
    processed_data = output.getvalue()
    return processed_data

# Streamlit interface setup
st.title('BMS Report Cleaner - Job Listing Report')


with st.expander("How do I run the report?"):
    st.write('1. Navigate to the "Job Listing" report (found under "Job Analysis" in BMS)')
    st.write('2. Set the "Date" selector to "Returned"')
    st.write('3. Set the "From Date" selector to the first day of the month')
    st.write("4. Set the 'To Date' selector to yesterday's date")
    st.write('5. Click "Print" then close the excel file that opens (you can save it somewhere if you want)')
    st.write('6. Come back to this page and upload the file (it should start with "job_list" and end with ".csv")')


uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])


# When a file is uploaded, process and display the data
if uploaded_file is not None:
    # Process file
    processed_data = process_data(uploaded_file)

    # Show processed data
    st.write("Processed Data:")
    st.dataframe(processed_data.head())

    # Download button for processed data as Excel
    st.download_button(
        label="Download Excel file",
        data=to_excel(processed_data),
        file_name="processed_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
    

    # Convert processed DataFrame to CSV format
    #processed_csv_data = to_csv_bytes(processed_data)

    # Push to GitHub
    #push_to_github(processed_csv_data, "processed_data.csv", "tdambrowitz/KPIs-and-Stats")

    #st.write("Data pushed to GitHub")
