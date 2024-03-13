# Import packages
import pyhrv.time_domain as td
import numpy as np
import sys
from sklearn.mixture import GaussianMixture
from scipy.stats import kurtosis

# Load sample data
nni_data = np.loadtxt(sys.argv[1]) * 1000

# Remove anomalies based on a specified range
min_nni = 300  # Minimum valid NNI value
max_nni = 1200  # Maximum valid NNI value
nni_data = nni_data[(nni_data >= min_nni) & (nni_data <= max_nni)]

# Check if there are enough samples after removing anomalies
min_samples = 3  # Minimum number of samples required for GMM (e.g. 1 min arrhy)
if len(nni_data) < min_samples:
    print(f"Insufficient samples ({len(nni_data)}) after removing anomalies. Skipping GMM fitting.")
else:
    # Reshape the data for GMM
    nni_data = nni_data.reshape(-1, 1)

    # Fit GMMs with different numbers of components
    n_components_range = range(1, 4)  # Range of components to try (1 to 3)
    bic_values = []

    for n_components in n_components_range:
        gmm = GaussianMixture(n_components=n_components)
        gmm.fit(nni_data)
        bic_values.append(gmm.bic(nni_data))

    # Find the optimal number of components based on BIC
    best_n_components = n_components_range[np.argmin(bic_values)]

    print(f"Optimal number of distributions: {best_n_components}")

    # Fit the GMM with the optimal number of components
    best_gmm = GaussianMixture(n_components=best_n_components)
    best_gmm.fit(nni_data)

    # Get the number of samples assigned to each distribution
    labels = best_gmm.predict(nni_data)
    sample_counts = np.bincount(labels)

    # Ignore distributions with fewer than 60 samples
    valid_distributions = sample_counts >= 60
    num_valid_distributions = np.sum(valid_distributions)

    if num_valid_distributions == 0:
        print("No valid distributions found (all distributions have fewer than 60 samples).")
    else:
        print(f"Number of valid distributions: {num_valid_distributions}")

        if num_valid_distributions == 1:
            print("The NNI data likely follows a single distribution.")
        else:
            print(f"The NNI data likely follows {num_valid_distributions} distributions.")

        # Calculate and print kurtosis, 1-SD, and 2-SD for each valid distribution
        for i in range(best_n_components):
            if valid_distributions[i]:
                distribution_data = nni_data[labels == i]
                distribution_kurtosis = kurtosis(distribution_data, fisher=False)[0]  # Access the first element of the array
                distribution_mean = np.mean(distribution_data)
                distribution_std = np.std(distribution_data)
                print(f"Distribution {i+1}:")
                print(f"  Kurtosis: {distribution_kurtosis:.2f}")
                print(f"  Mean: {distribution_mean:.2f} ms")
                print(f"  Standard Deviation: {distribution_std:.2f} ms")
                print(f"  1-SD Range: [{distribution_mean - distribution_std:.2f}, {distribution_mean + distribution_std:.2f}] ms")
                print(f"  2-SD Range: [{distribution_mean - 2*distribution_std:.2f}, {distribution_mean + 2*distribution_std:.2f}] ms")

        # Plot the histogram and the fitted distributions
        import matplotlib.pyplot as plt

        plt.figure(figsize=(8, 6))
        plt.hist(nni_data, bins=50, density=True, alpha=0.6, color='b')

        x = np.linspace(nni_data.min(), nni_data.max(), 1000)
        for i in range(best_n_components):
            if valid_distributions[i]:
                mu, std = best_gmm.means_[i][0], np.sqrt(best_gmm.covariances_[i][0][0])
                y = np.exp(-0.5 * ((x - mu) / std)**2) / (std * np.sqrt(2 * np.pi))
                plt.plot(x, y, label=f"Distribution {i+1}")

        plt.xlabel('NNI Bins [ms]')
        plt.ylabel('Density')
        plt.title('NNI Histogram with Fitted Distributions (Anomalies Removed)')
        plt.legend()
        plt.tight_layout()
        plt.show()
