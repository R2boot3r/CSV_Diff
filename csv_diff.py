import pandas as pd
import numpy as np
from tabulate import tabulate
from colorama import Fore, Back, Style, init

def load_csv_files(file1_path, file2_path):
    """Load two CSV files into pandas DataFrames."""
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)
    return df1, df2

def find_differences(df1, df2):
    """Find differences between two DataFrames."""
    # Ensure both DataFrames have the same columns
    all_columns = list(set(df1.columns) | set(df2.columns))
    
    # Add missing columns with NaN values
    for col in all_columns:
        if col not in df1.columns:
            df1[col] = np.nan
        if col not in df2.columns:
            df2[col] = np.nan
    
    # Find different values
    differences = []
    for idx in range(max(len(df1), len(df2))):
        if idx < len(df1) and idx < len(df2):
            row1 = df1.iloc[idx]
            row2 = df2.iloc[idx]
            
            for col in all_columns:
                val1 = row1[col]
                val2 = row2[col]
                
                # Check if values are different (considering NaN)
                if pd.isna(val1) and pd.isna(val2):
                    continue
                elif pd.isna(val1) or pd.isna(val2) or val1 != val2:
                    differences.append({
                        'row': idx,
                        'column': col,
                        'old_value': val1,
                        'new_value': val2
                    })
        else:
            # Handle cases where one DataFrame is longer
            if idx >= len(df1):
                row2 = df2.iloc[idx]
                for col in all_columns:
                    differences.append({
                        'row': idx,
                        'column': col,
                        'old_value': np.nan,
                        'new_value': row2[col]
                    })
            else:
                row1 = df1.iloc[idx]
                for col in all_columns:
                    differences.append({
                        'row': idx,
                        'column': col,
                        'old_value': row1[col],
                        'new_value': np.nan
                    })
    
    return differences

def display_difference(diff, df1, df2):
    """Display a single difference with context."""
    row = diff['row']
    col = diff['column']
    
    # Get the row data for context
    row_data1 = df1.iloc[row] if row < len(df1) else pd.Series([np.nan] * len(df1.columns), index=df1.columns)
    row_data2 = df2.iloc[row] if row < len(df2) else pd.Series([np.nan] * len(df2.columns), index=df2.columns)
    
    print(f"\nRow {row + 1}, Column: {col}")
    print(f"Old value: {Fore.RED}{diff['old_value']}{Style.RESET_ALL}")
    print(f"New value: {Fore.GREEN}{diff['new_value']}{Style.RESET_ALL}")
    
    # Show row context
    context_data = []
    for column in df1.columns:
        old_val = row_data1[column]
        new_val = row_data2[column]
        if column == col:
            old_val = f"{Fore.RED}{old_val}{Style.RESET_ALL}"
            new_val = f"{Fore.GREEN}{new_val}{Style.RESET_ALL}"
        context_data.append([column, old_val, new_val])
    
    print("\nRow context:")
    print(tabulate(context_data, headers=['Column', 'Old Value', 'New Value'], tablefmt='grid'))

def interactive_diff(file1_path, file2_path):
    """Main function to handle interactive diffing."""
    init()  # Initialize colorama
    
    print(f"Comparing {file1_path} with {file2_path}")
    
    # Load CSV files
    df1, df2 = load_csv_files(file1_path, file2_path)
    result_df = df1.copy()
    
    # Find differences
    differences = find_differences(df1, df2)
    
    if not differences:
        print("No differences found between the files.")
        return
    
    print(f"\nFound {len(differences)} differences.")
    
    # Process each difference
    for i, diff in enumerate(differences, 1):
        print(f"\nDifference {i} of {len(differences)}")
        display_difference(diff, df1, df2)
        
        while True:
            choice = input("\nAccept this change? (y/n/q to quit): ").lower()
            if choice in ['y', 'n', 'q']:
                break
            print("Invalid input. Please enter 'y' for yes, 'n' for no, or 'q' to quit.")
        
        if choice == 'q':
            print("Exiting...")
            break
        
        if choice == 'y':
            # Apply the change to result_df
            result_df.at[diff['row'], diff['column']] = diff['new_value']
    
    # Save the result
    output_path = 'merged_result.csv'
    result_df.to_csv(output_path, index=False)
    print(f"\nSaved merged result to {output_path}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python csv_diff.py <file1.csv> <file2.csv>")
        sys.exit(1)
    
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    
    interactive_diff(file1_path, file2_path) 