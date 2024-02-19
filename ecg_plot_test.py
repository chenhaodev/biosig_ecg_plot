from scipy.io import loadmat
import ecg_plot

def load_ecg_from_mat(file_path):
    mat = loadmat(file_path)
    data = mat["data"]
    feature = data[0:12]
    return(feature)

ecg = load_ecg_from_mat('example_ecg.mat')

ecg_plot.plot_12(ecg, sample_rate=500, title='12 lead EKG')
ecg_plot.save_as_png('example_ecg_12_lead')

ecg_plot.plot_1(ecg[1], sample_rate=500, title = 'lead-II EKG')
ecg_plot.save_as_png('example_ecg_lead_ii')
