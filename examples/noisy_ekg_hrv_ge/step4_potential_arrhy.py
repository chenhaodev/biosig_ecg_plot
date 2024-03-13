import os
import re

def is_abnormal(filename):
    """Check if the file content meets the abnormal criteria."""
    with open(filename, 'r') as file:
        content = file.read()

        # Find all instances of distributions mentioned and their kurtosis values
        distributions = re.findall(r'The NNI data likely follows (\d+) distributions', content)
        kurtosis_values = re.findall(r'Kurtosis: ([\d.]+)', content)

        # Check the criteria for being abnormal
        if distributions:
            num_distributions = int(distributions[0])
            if num_distributions >= 2:
                return True
            elif num_distributions == 1 and kurtosis_values:
                if float(kurtosis_values[0]) < 3.5:
                    return True
        return False

def list_abnormal_filenames():
    """List filenames that meet the abnormal criteria."""
    abnormal_filenames = []

    # Iterate through all files in the current directory
    for filename in os.listdir('.'):
        if os.path.isfile(filename):
            if is_abnormal(filename):
                abnormal_filenames.append(filename)

    return abnormal_filenames

# Execute the function and print out the abnormal filenames
abnormal_filenames = list_abnormal_filenames()
for filename in abnormal_filenames:
    print(filename)
