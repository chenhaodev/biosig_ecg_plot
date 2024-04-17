import pandas as pd

def replace_text(value, allowed_values):
    if pd.isna(value) or value not in allowed_values:
        return 'Unknown'  # Replace with an appropriate default value
    return value

def replace_nsr(value_list):
    if 'NSR' in value_list:
        if any(condition in value_list for condition in ['AFIB', 'Tachycardia', 'Bradycardia']):
            value_list.remove('NSR')
    return value_list

def process_data(input_file, output_file):
    try:
        df_csv = pd.read_csv(input_file)
        
        if 'Arrhythmia' not in df_csv.columns:
            raise KeyError("Column 'Arrhythmia' not found in the input file.")
        
        # Replace specific values in the 'Arrhythmia' column
        replacements = {
            'Atrial Fibrillation': 'AFIB',
            'Sinus rhythm': 'NSR',
            'V.Bigeminy': 'Vbig',
            'A.Bigeminy': 'Vbig',
            'V.Trigeminy': 'Vtrig',
            'Sinus bradycardia': 'Bradycardia',
            'Sinus tachycardia': 'Tachycardia',
            'PAC': 'PVC',
            'Interpolated PVC': 'PVC',
            'PVC,': 'PVC'
        }
        df_csv['Arrhythmia'] = df_csv['Arrhythmia'].replace(replacements)
        
        # Remove non-detected arrhythmia
        unique_annotation = ['AFIB', 'NSR', 'Vbig', 'Vtrig', 'PVC', 'Pause', 'Bradycardia', 'Tachycardia']
        
        def process_arrhythmia(row):
            try:
                return replace_text(row['Arrhythmia'], unique_annotation)
            except KeyError as e:
                print(f"Error processing row {row.name + 2}: {str(e)}")
                return 'Unknown'
        
        df_csv['Arrhythmia'] = df_csv.apply(process_arrhythmia, axis=1)
        
        # Group by 'ID' and aggregate 'Arrhythmia' values into a list
        df_csv = df_csv.groupby('ID')['Arrhythmia'].agg(list).reset_index()
        
        # Remove duplicate values from the 'Arrhythmia' list
        df_csv['Arrhythmia'] = df_csv['Arrhythmia'].apply(lambda x: list(set(x)))
        
        # Apply the replace_nsr function to the 'Arrhythmia' list
        df_csv['Arrhythmia'] = df_csv['Arrhythmia'].apply(replace_nsr)
        
        # Save the processed data to a new CSV file
        df_csv.to_csv(output_file, index=False)
        
        print(f"Data processed successfully. Output saved to {output_file}")
    
    except FileNotFoundError:
        print(f"Input file '{input_file}' not found.")
    
    except KeyError as e:
        print(f"Error: {str(e)}")
        print("Please ensure that the 'Arrhythmia' column exists in the input file.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Specify the input and output file paths
input_file = 'samsung_2nd_round_data_20240308_cut.csv'
output_file = 'api_samsung_01042024.csv'

# Process the data
process_data(input_file, output_file)