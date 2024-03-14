# Import packages
import os
import pyhrv.time_domain as td
import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import kurtosis

# Get the list of files with '.nni.txt' extension in the current directory
nni_files = [file for file in os.listdir() if file.endswith('.nni.txt')]

# Process each NNI file
for nni_file in nni_files:
    # Load sample data
    nni_data = np.loadtxt(nni_file) * 1000

    # Remove anomalies based on a specified range
    min_nni = 300  # Minimum valid NNI value
    max_nni = 1200  # Maximum valid NNI value
    nni_data = nni_data[(nni_data >= min_nni) & (nni_data <= max_nni)]

    # Open a file for writing the output
    output_file = nni_file.replace('.nni.txt', '.nna.txt')
    print(f"Analysis results for {nni_file} saved to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        # Check if there are enough samples after removing anomalies
        min_samples = 3  # Minimum number of samples required for GMM (e.g. 1 min arrhy)
        if len(nni_data) < min_samples:
            f.write(f"Insufficient samples ({len(nni_data)}) after removing anomalies. Skipping GMM fitting.\n")
        else:
            # Reshape the data for GMM
            nni_data = nni_data.reshape(-1, 1)

            # Fit GMMs with different numbers of components
            n_components_range = range(1, 3)  # Range of components to try (1 to 2)
            bic_values = []

            for n_components in n_components_range:
                gmm = GaussianMixture(n_components=n_components)
                gmm.fit(nni_data)
                bic_values.append(gmm.bic(nni_data))

            # Find the optimal number of components based on BIC
            best_n_components = n_components_range[np.argmin(bic_values)]

            f.write(f"Optimal number of distributions: {best_n_components}\n")

            # Fit the GMM with the optimal number of components
            best_gmm = GaussianMixture(n_components=best_n_components)
            best_gmm.fit(nni_data)

            # Get the number of samples assigned to each distribution
            labels = best_gmm.predict(nni_data)
            sample_counts = np.bincount(labels)

            # Ignore distributions with fewer than 30 samples
            valid_distributions = sample_counts >= 30
            num_valid_distributions = np.sum(valid_distributions)

            if num_valid_distributions == 0:
                f.write("No valid distributions found (all distributions have fewer than 30 samples).\n")
            else:
                f.write(f"Number of valid distributions: {num_valid_distributions}\n")

                if num_valid_distributions == 1:
                    f.write("The NNI data likely follows 1 distribution.\n")
                else:
                    f.write(f"The NNI data likely follows {num_valid_distributions} distributions.\n")

                # Calculate and print kurtosis, 1-SD, and 2-SD for each valid distribution
                for i in range(best_n_components):
                    if i < len(valid_distributions) and valid_distributions[i]:
                        distribution_data = nni_data[labels == i]
                        distribution_kurtosis = kurtosis(distribution_data, fisher=False)[0]
                        distribution_mean = np.mean(distribution_data)
                        distribution_std = np.std(distribution_data)
                        f.write(f"Distribution {i+1}:\n")
                        f.write(f"  Kurtosis: {distribution_kurtosis:.2f}\n")
                        f.write(f"  Mean: {distribution_mean:.2f} ms\n")
                        f.write(f"  Standard Deviation: {distribution_std:.2f} ms\n")
                        f.write(f"  1-SD Range: [{distribution_mean - distribution_std:.2f}, {distribution_mean + distribution_std:.2f}] ms\n")
                        f.write(f"  2-SD Range: [{distribution_mean - 2*distribution_std:.2f}, {distribution_mean + 2*distribution_std:.2f}] ms\n")

