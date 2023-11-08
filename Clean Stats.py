import pandas as pd
import re
import os
import numpy as np
from pandas.tseries.offsets import BDay
from datetime import datetime, timedelta, date
import shutil
os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = "C:\\Program Files\\Git\\bin\\git.exe"
import git
from calendar import monthrange

repo = git.Repo(r"C:\Users\trenton.dambrowitz\OneDrive - Halo ARC Ltd\Desktop\AI Stuff\KPIs and Stats")  # Replace with the path to your local repo


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

# Constants
folder_path = r'C:\Users\trenton.dambrowitz\OneDrive - Halo ARC Ltd\Desktop\AI Stuff\KPIs and Stats'

# Find the most recent CSV file
def find_most_recent_csv_file(folder_path, file_prefix):
    csv_files = [f for f in os.listdir(folder_path) if f.startswith(file_prefix) and f.endswith(".csv")]
    
    # If there are no matching csv files, return None
    if not csv_files:
        return None
    
    # Sort the files based on modification time in descending order
    most_recent_csv = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(folder_path, f)))
    return os.path.join(folder_path, most_recent_csv)

# Replace 'job_list' with your actual input file prefix
csv_file_path = find_most_recent_csv_file(folder_path, "job_list")
# Replace 'output_file.csv' with your desired output file name
output_file = 'output_file.csv'

if csv_file_path:
    # Read the .csv file into a DataFrame
    df = pd.read_csv(csv_file_path, skiprows=2)

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
    current_date = datetime.now().date()
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

    # Month mapping
    month_mapping = {
        '01': 'JANUARY', '02': 'FEBRUARY', '03': 'MARCH', '04': 'APRIL',
        '05': 'MAY', '06': 'JUNE', '07': 'JULY', '08': 'AUGUST',
        '09': 'SEPTEMBER', '10': 'OCTOBER', '11': 'NOVEMBER', '12': 'DECEMBER'
    }

    # Getting current month and year from 'Left Site Date/Time'
    # Check the data type of the column
    extracted_data['Left Site Date/Time'] = pd.to_datetime(extracted_data['Left Site Date/Time'], format=datetime_format, errors='coerce')
    print(extracted_data['Left Site Date/Time'].dtypes)

    unique_dates = extracted_data['Left Site Date/Time'].dropna().dt.to_period("M").unique()
    most_recent_date = unique_dates.max()
    current_month = most_recent_date.month
    current_year = most_recent_date.year

    # Map month number to month name
    current_month_str = f"{current_month:02d}"
    current_month_name = month_mapping[current_month_str]

    # Last day of the "current" month
    _, last_day = monthrange(current_year, current_month)

    # All days in the "current" month
    all_days = pd.date_range(start=f"{current_year}-{current_month}-01", end=f"{current_year}-{current_month}-{last_day}")

    # Filter out weekends to get working days
    working_days = all_days.to_series().loc[lambda x: ~x.dt.dayofweek.isin([5, 6])].dt.date

    # Convert working_days to a list
    working_days_list = working_days.tolist()

    # Print the list for your reference (you can remove this line later)
    #st.write("Working Days List:", working_days_list)
    
    # Manually remove specific dates
    # Example dates to remove
    #dates_to_remove = [date(2023, 8, 28)]

    # Remove them from the working_days_list
    #for dt in dates_to_remove:
        #if dt in working_days_list:
            #working_days_list.remove(dt)
    working_days_map = {i+1: dt for i, dt in enumerate(working_days_list)}
    days_count = working_days_list.count(1)
    #st.write(working_days_map)
    site_targets = {
        'Poole (B)': 88, 'Westbury (C)': 88, 'Eastleigh (H)': 88, 'Chandlers (I)': 88, 'Basingstoke (J)': 88,
        'Cheltenham (L)': 88, 'Bournemouth (M)': 88, 'Portsmouth (N)': 88, 'Stoke (O)': 88, 'Eastbourne (P)': 88,
        'Shoreham (Q)': 88, 'Amesbury (R)': 88, 'Swindon (T)': 88, 'Lincoln (U)': 88, 'Wakefield (V)': 88,
        'Guildford (W)': 88, 'York (X)': 88, 'Harrow (Y)': 88,
        'Bognor (A)': 100, 'Bristol (K)': 100, 'Cardiff (E)': 99, 'Crewe (F)': 99, 'Innovation (A)': 88,
        'Trafford (S)': 100, 'West Thurrock (Z)': 88
    }
    

    extracted_data.loc[:, 'Left Site Date/Time'] = pd.to_datetime(extracted_data['Left Site Date/Time'], errors='coerce')
    extracted_data['Left Site Date/Time'] = pd.to_datetime(extracted_data['Left Site Date/Time'], errors='coerce')

    #print(extracted_data['Left Site Date/Time'].dtypes)



    completed_jobs = extracted_data[extracted_data['Left Site Date/Time'].dt.month == current_month].copy()

    # 2. Adjust completion dates for jobs completed on weekends to the preceding Friday
    completed_jobs['Completion Date'] = completed_jobs['Left Site Date/Time'].dt.date
    completed_jobs['Completion Date'] = pd.to_datetime(completed_jobs['Completion Date'])

    completed_jobs['Weekday'] = completed_jobs['Left Site Date/Time'].dt.weekday
    completed_jobs['Weekday'] = completed_jobs['Weekday'].astype(int)

    completed_jobs['Completion Date'] = np.where(
        completed_jobs['Weekday'] >= 5,
        completed_jobs['Completion Date'] - pd.to_timedelta(completed_jobs['Weekday'] - 4, unit='D'),
        completed_jobs['Completion Date']
    )
    #print(completed_jobs)

    # 3. Count cumulative number of jobs completed for each day
    overall_cumulative_count = completed_jobs.groupby('Completion Date').size().cumsum().reset_index(name='Cumulative Count')
    #print(overall_cumulative_count)

        # Calculate the total target for all sites
    total_target = sum(site_targets.values())

    # Calculate incremental target values for the total target
    n_working_days = len(working_days_map)
    total_increment = total_target / n_working_days
    total_incremental_target_values = np.linspace(total_increment, total_target, n_working_days)
    # Calculate projection for the overall data
    
    last_completion_date = overall_cumulative_count['Completion Date'].max()

    
    #print(last_completion_date)
    
    #print(overall_cumulative_count['Completion Date'])
    #print(
    #print(overall_cumulative_count['Completion Date'].unique())
    #print("Last completion date:", last_completion_date)


    filtered_values = overall_cumulative_count.loc[overall_cumulative_count['Completion Date'] == last_completion_date, 'Cumulative Count'].values
    
    #print(filtered_values)

    if len(filtered_values) > 0:
        mtd_average = filtered_values[0] / len(overall_cumulative_count)
    else:
        mtd_average = 0  # or whatever default value you want to use

    #print(mtd_average)

        # Convert Timestamp to datetime.date for the comparison
    last_completion_date_date = last_completion_date.to_pydatetime().date()
    #print(last_completion_date_date)
    last_completion_date_idx = working_days_list.index(last_completion_date_date)



    remaining_days = [working_days_map[k] for k in working_days_map.keys() if working_days_map[k] > last_completion_date_date]
    passed_days = [working_days_map[k] for k in working_days_map.keys() if working_days_map[k] <= last_completion_date_date]
    days_gone = len(passed_days)
    #print(days_gone)
    #print(remaining_days)
    #print(passed_days)


    projected_values = [overall_cumulative_count['Cumulative Count'].iloc[-1] + mtd_average * (i + 1) for i in range(len(remaining_days))]
    #print(projected_values)


    # Interpolate missing data points using forward fill
    interpolated_main_line_data = overall_cumulative_count.set_index('Completion Date').reindex(working_days_list).ffill().fillna(0).reset_index()
    #print(interpolated_main_line_data)
    # Find the index of the last completion date in working_days_list
    working_days_list_timestamps = [pd.Timestamp(date) for date in working_days_list]
    last_completion_date_idx = working_days_list_timestamps.index(last_completion_date)
    # Trim the main line data to stop at the last completion date
    trimmed_main_line_data = interpolated_main_line_data.iloc[:last_completion_date_idx + 1]

    #print(trimmed_main_line_data)
    # Initialize a list to store the overall group data for MTD Avg Key to Key
    overall_mtd_avg_key_to_key_list = []
    #print(working_days_list)
    for date in passed_days:
        if date <= pd.Timestamp.today().date():  # Filter out future dates
            # Filter data up to the current working day
            filtered_data = completed_jobs[completed_jobs['Completion Date'] <= pd.Timestamp(date)]
            #print(filtered_data)


            # Calculate the mean Key to Key time for jobs completed up to this date
            mean_key_to_key = filtered_data['Key to Key'].mean()

            # Append to the list
            overall_mtd_avg_key_to_key_list.append({'Completion Date': date, 'Overall MTD Avg Key to Key': mean_key_to_key})

    # Convert list of dictionaries to DataFrame
    overall_mtd_avg_key_to_key = pd.DataFrame(overall_mtd_avg_key_to_key_list)
    print(overall_mtd_avg_key_to_key)

    locations = completed_jobs['Location'].unique()
    n_locations = len(locations)  # Make sure this line is before n_rows
    #print(n_locations)#


            # Initialize a dictionary to store the variance from MTD target for each location
    variance_from_mtd_target = []
    target_for_units = {}

    filtered_jobs = completed_jobs[completed_jobs['Completion Date'] <= pd.Timestamp(date)]
    #print(days_gone)
    # Calculate the total number of working days in the month
    total_working_days = len(working_days_map)

    site_key_to_keys = []
    
    for location in locations:

        #print(location)
        location_data = filtered_jobs[filtered_jobs['Location'] == location]

                    # Calculate the mean Key to Key time for jobs completed up to this date
        mean_key_to_key = location_data['Key to Key'].mean()

            # Append to the list
        site_key_to_keys.append({f'{location}': mean_key_to_key})
        #print(site_key_to_keys)

        location_data = completed_jobs[completed_jobs['Location'] == location]
        #print(location_data)
        location_cumulative_count = location_data.groupby('Completion Date').size().cumsum().reset_index(name='Cumulative Count')
        #print(location_cumulative_count)
        location_target = site_targets.get(location, 0)
        # Calculate incremental target values
        n_working_days = len(working_days_map)
        increment = location_target / n_working_days
        incremental_target_values = np.linspace(increment, location_target, n_working_days)
        #print(incremental_target_values)

        # Calculate projection
        last_completion_date = location_cumulative_count['Completion Date'].max()
        mtd_average = location_cumulative_count.loc[location_cumulative_count['Completion Date'] == last_completion_date, 'Cumulative Count'].values[0] / len(location_cumulative_count)
        projected_values = [location_cumulative_count['Cumulative Count'].iloc[-1] + mtd_average * (i) for i in range(len(remaining_days))]
        #print(projected_values)
        #print(mtd_average)

        
        
        
        mtd_units = len(location_data)
        #print(mtd_units)
        #print(len(location_data))
        # Calculate the scaled down target based on the last completion date
        scaled_down_target = round(site_targets[location] * ((days_gone - 0) / total_working_days), 2)

        #print(scaled_down_target)
        # Get the last available cumulative count
        #last_cumulative_count = location_cumulative_count['Cumulative Count'].iloc[-1]
        
        #print(last_cumulative_count)
        # Calculate the variance from the scaled down target
        variance = round(mtd_units - scaled_down_target, 2)
        #print(variance)
        #st.write(variance)
        # Store the variance in the dictionary
        variance_from_mtd_target.append({f'{location}': variance})
        # If no completion date is available, set variance to negative target (indicating full variance)


    #print(site_key_to_keys)
    #print(variance_from_mtd_target)

    # Convert list of dictionaries to DataFrames and then melt them
    df_site_key_to_keys = pd.DataFrame(site_key_to_keys).apply(lambda x: pd.Series(x.dropna().to_dict()), axis=1).reset_index(drop=True).melt(var_name='Site', value_name='Site Key to Keys')
    #df_site_key_to_keys = pd.DataFrame(index=branch_order)
    #print(df_site_key_to_keys)
    
    df_variance_from_mtd_target = pd.DataFrame(variance_from_mtd_target).apply(lambda x: pd.Series(x.dropna().to_dict()), axis=1).reset_index(drop=True).melt(var_name='Site', value_name='Variance from MTD Target')

    #df_variance_from_mtd_target = pd.DataFrame(index=branch_order)
    #print(df_variance_from_mtd_target)


    # Merge the two DataFrames
    merged_df = pd.merge(df_site_key_to_keys, df_variance_from_mtd_target, on='Site')

    # Drop rows where either 'Site Key to Keys' or 'Variance from MTD Target' is NaN
    merged_df.dropna(subset=['Site Key to Keys', 'Variance from MTD Target'], inplace=True)

    # Sort merged_df based on branch_order
    merged_df['Site'] = pd.Categorical(merged_df['Site'], categories=branch_order, ordered=True)
    merged_df = merged_df.sort_values('Site')

    # Write to Excel
    with pd.ExcelWriter('site_key_to_keys_and_variances.xlsx') as writer:
        merged_df.to_excel(writer, index=False, sheet_name='Sheet1')







    # Save the cleaned DataFrame to a new .csv file
    df.to_csv(output_file, index=False)
    
else:
    print("No matching CSV files found.")


# Replace 'job_list' with your actual input file prefix
csv_file_path = find_most_recent_csv_file(folder_path, "finance")


branch_mapping2 = {
    'A': 'Bognor (A)',
    'B': 'Poole (B)',
    'C': 'Westbury (C)',
    'D': 'Innovation (D)',
    'E': 'Cardiff (E)',
    'F': 'Crewe (F)',
    'H': 'Eastleigh (H)',
    'N': 'Portsmouth (N)',
    'P': 'Eastbourne (P)',
    'R': 'Amesbury (R)',
    'I': 'Chandlers (I)',
    'J': 'Basingstoke (J)',
    'K': 'Bristol (K)',
    'L': 'Cheltenham (L)',
    'M': 'Bournemouth (M)',
    'O': 'Stoke (O)',
    'Q': 'Shoreham (Q)',
    'S': 'Trafford (S)',
    'T': 'Swindon (T)',
    'U': 'Lincoln (U)',
    'V': 'Wakefield (V)',
    'W': 'Guildford (W)',
    'X': 'York (X)',
    'Y': 'Harrow (Y)',
    'Z': 'West Thurrock (Z)'
}



if csv_file_path:
    # Read the .csv file into a DataFrame
    sales_df = pd.read_csv(csv_file_path, skiprows=2)
    
    # Remove all empty rows
    sales_df.dropna(how='all', inplace=True)

    # Remove rows where the first cell doesn't start with a letter followed by a number
    sales_df = sales_df[sales_df[sales_df.columns[0]].apply(lambda x: re.match(r'^[A-Za-z][0-9]', str(x)) is not None)]
    
    # Reset index for cleaner output
    sales_df.reset_index(drop=True, inplace=True)

    # Create a new "Branch" column by extracting the first letter of the job number and mapping it
    sales_df['Branch'] = sales_df[sales_df.columns[0]].apply(lambda x: branch_mapping2.get(str(x)[0].upper()))

    print(sales_df)
    sales_df.to_csv("sales.csv", index=False)

    
sales_df.to_csv('output_file_path.csv', index=False)





def push_files_to_github():
    repo_path = "C:\\Users\\trenton.dambrowitz\\OneDrive - Halo ARC Ltd\\Desktop\\AI Stuff\\KPIs and Stats"  # Your repo path
    repo = git.Repo(repo_path)

    files_to_add = ['output_file.csv', 'site_key_to_keys_and_variances.xlsx']
    for file_name in files_to_add:
        file_path = os.path.join(repo_path, file_name)
        repo.git.add(file_path)

    # Commit the changes
    repo.git.commit("-m", "Automatically added files")

    # Force push the changes
    try:
        repo.git.push("--force", "origin", "main")
        print("Files successfully force-pushed to github repo")
    except git.exc.GitCommandError as error:
        print(f"Git push failed: {error}")

# Run the function
push_files_to_github()

print("Files successfully pushed to github repo")
