import pickle
import os
import numpy as np
from sklearn.decomposition import PCA

# This script combines magnitude with phase of FT image before it should be sent to PCA_final for PCA.
# This is not usually performed if refined scale is active, as magnitude has enough information for PCA.

'''User Input'''

# Must contain Fourier Transformed Images, ft_data. Also ouputs PCA_data in the same folder.
load_path = r"C:\Users\Han Xuan\Desktop\OneDrive - Imperial College London\Attachments\Input Storage\Simulations\33m ML\Fourier Transformed Scaled"
n_components = "Max"

'''End User Input'''


def main(n_components):

    obj_input_path = os.path.join(load_path, "ft_data")
    with open(obj_input_path, 'rb') as pickleFile:
        magnitudes, phases, f_list = pickle.load(pickleFile)

    magnitudes = np.asarray(magnitudes)  # No logarithm
    if n_components == "Max":
        n_components = magnitudes.shape[0]

    x = np.reshape(magnitudes, (magnitudes.shape[0], magnitudes.shape[1] * magnitudes.shape[2]))
    pca = PCA(n_components=n_components, svd_solver='full', whiten=False).fit(x)
    magnitudes_pca = pca.transform(x)
    mag_eigens = pca.components_.reshape((n_components, magnitudes.shape[1], magnitudes.shape[2]))

    phases = np.asarray(phases)
    x2 = np.reshape(phases, (phases.shape[0], phases.shape[1] * phases.shape[2]))
    pca = PCA(n_components=n_components, svd_solver='full', whiten=False).fit(x2)
    phases_pca = pca.transform(x2)
    phases = pca.components_.reshape((n_components, phases.shape[1], phases.shape[2]))

    f_shift_recon = np.empty((mag_eigens.shape[0], mag_eigens.shape[1], mag_eigens.shape[2]), dtype=np.complex)
    # f_shift_recon[0][0][0] = magnitudes[0][0][0]*np.exp(1j*phases[0][0][0])
    # print(f_shift_recon[0][0][0])

    for a in range(f_shift_recon.shape[0]):
        for b in range(f_shift_recon.shape[1]):
            for c in range(f_shift_recon.shape[2]):
                f_shift_recon[a][b][c] = mag_eigens[a][b][c]*np.exp(1j*phases[a][b][c])

    # dump with pickle
    obj_output_path = os.path.join(load_path, "ft_PCA_data")
    with open(obj_output_path, 'wb') as pickleFile:
        pickle.dump((f_shift_recon, mag_eigens), pickleFile)


if __name__ == "__main__":
    main(n_components)