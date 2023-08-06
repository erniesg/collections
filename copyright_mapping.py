import pandas as pd
import datetime

# Mapping function
def map_rights(row):
    # Initial default values
    cleaned_status = ""
    educational_use = "No"
    marketing_use = "No"
    commercial_use = "No"
    sublicensing_use = "No"
    notes = ""
    
    # Map based on the provided rights
    if "CF" in str(row['Rights']):
        cleaned_status = "All permissions"
        educational_use = "Yes"
        marketing_use = "Yes"
        commercial_use = "Yes"
        sublicensing_use = "Yes"
        notes = "Rights owner signed a license that allows all reproductions."
    elif "CL" in str(row['Rights']):
        cleaned_status = "Limited permissions"
        educational_use = "Yes"
        marketing_use = "Yes"
        commercial_use = "Restricted"
        notes = "Rights owner signed a license that allows most reproductions (usually restricted to non-commercial uses only)."
    elif "CE" in str(row['Rights']) or "Out of IP protection" in str(row['Rights']):
        cleaned_status = "All permissions"
        educational_use = "Yes"
        marketing_use = "Yes"
        commercial_use = "Yes"
        sublicensing_use = "Yes"
        notes = "Copyright is expired."
    elif "NC" in str(row['Rights']) or "N1" in str(row['Rights']) or "N2" in str(row['Rights']) or "Processing" in str(row['Rights']):
        cleaned_status = "Case-by-case review"
        notes = "Usually there is no licence deed signed as we couldn’t contact/find the rights owner, or they did not respond."
    elif "D" in str(row['Rights']) or "DP" in str(row['Rights']):
        cleaned_status = "Denied"
        notes = "Copyright holder has denied the use of artwork image for any Gallery use."
    elif "Full transfer of rights" in str(row['Rights']):
        cleaned_status = "All permissions"
        educational_use = "Yes"
        marketing_use = "Yes"
        commercial_use = "Yes"
        sublicensing_use = "Yes"
        notes = "In the past, rights owners sometimes transferred their rights to the copyright to NHB."
    elif "Non-Exclusive license" in str(row['Rights']) or "Exclusive license" in str(row['Rights']):
        cleaned_status = "As per SCMS notes"
        notes = "A license was signed (via NHB). Specific permissions are determined by SCMS notes."
    elif pd.isnull(row['Rights']):
        cleaned_status = "Not available"
        notes = "We don’t have a license, or the ‘Rights’ field has not been updated."
    elif "Record of Effort (RoE)" in str(row['Rights']):
        cleaned_status = "RoE"
        notes = "You may find references to a ‘Record of Effort’ (ROE) form in the Remarks field."
    else:
        cleaned_status = "Other"
        notes = str(row['Rights'])
    
    return pd.Series([cleaned_status, educational_use, marketing_use, commercial_use, sublicensing_use, notes])

# Correcting the verification and summarization function
def verify_and_summarize(data, map_rights):
    unique_rights_values = data['Rights'].dropna().unique()
    
    # Randomly sample one row for each unique value from the 'Rights' column
    test_rows = [data[data['Rights'] == value].sample(1).iloc[0] for value in unique_rights_values]
    # Including a row with NaN (to represent BLANK value)
    test_rows.append(data[data['Rights'].isnull()].sample(1).iloc[0])
    
    test_data = pd.DataFrame(test_rows)
    
    # Compute expected results by applying the map_rights function
    expected_results = test_data.apply(map_rights, axis=1)
    
    # Apply the mapping function to the sampled test dataframe
    actual_results = test_data.apply(map_rights, axis=1)
    
    passed_tests = 0
    failed_tests_data = []
    successful_sample = None
    
    # Verify the results by comparing expected vs actual
    for (idx, expected_row), (_, actual_row) in zip(expected_results.iterrows(), actual_results.iterrows()):
        if all(expected_row == actual_row):
            passed_tests += 1
            # Saving a sample successful result
            if successful_sample is None:
                successful_sample = test_data.loc[idx]  # <-- This line is corrected
                print(successful_sample)  # <-- Add this print statement here
        else:
            failed_row = test_data.loc[idx]
            failed_tests_data.append(failed_row)
    
    return passed_tests, successful_sample, failed_tests_data, len(test_data)

def main():
    # Loading the data
    data = pd.read_excel("../raw_data/artworks_cleaned_02082023.xlsx")

    # Apply the mapping function
    data[['Cleaned Copyright Status', 'Educational Use', 'Marketing/Publicity Use', 'Commercial Use', 'Sublicensing Use', 'Notes']] = data.apply(map_rights, axis=1)

    # Fetching the test cases, verifying, and summarizing the results
    passed_tests, successful_sample, failed_tests_data, total_tests = verify_and_summarize(data, map_rights)

    # Print the results
    print(f"\nOut of a total of {total_tests} unique test cases:")
    print(f"- {passed_tests} tests passed successfully.")
    print(f"- {total_tests - passed_tests} tests failed.\n")

    print("Sample successful result:")
    print("- Rights:", successful_sample['Rights'])
    print("- Cleaned Copyright Status:", successful_sample['Cleaned Copyright Status'])
    print("- Educational Use:", successful_sample['Educational Use'])
    print("- Marketing/Publicity Use:", successful_sample['Marketing/Publicity Use'])
    print("- Commercial Use:", successful_sample['Commercial Use'])
    print("- Sublicensing Use:", successful_sample['Sublicensing Use'])
    print("- Notes:", successful_sample['Notes'])

    if failed_tests_data:
        print("\nFailed results:")
        for failed_row in failed_tests_data:
            print("-" * 50)
            print("Rights:", failed_row['Rights'])
            print("Cleaned Copyright Status:", failed_row['Cleaned Copyright Status'])
            print("Educational Use:", failed_row['Educational Use'])
            print("Marketing/Publicity Use:", failed_row['Marketing/Publicity Use'])
            print("Commercial Use:", failed_row['Commercial Use'])
            print("Sublicensing Use:", failed_row['Sublicensing Use'])
            print("Notes:", failed_row['Notes'])
    else:
        print("\nNo failed results to display.")

    # Save the processed DataFrame as an Excel file
    today = datetime.date.today()
    data.to_excel(f'../raw_data/artworks_final_{today.strftime("%d%m%Y")}.xlsx', index=False)

if __name__ == "__main__":
    main()
