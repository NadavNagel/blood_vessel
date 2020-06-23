import numpy as np
import vtk as vtk
from vtk import vtkXMLUnstructuredGridReader
from vtk.util.numpy_support import vtk_to_numpy #thats what we need for saving the information into lists
from enum import Enum
import pickle
import os

class MeshType(Enum):
    VAN_MISES = 0
    DISPLACEMENT = 1
    STRAIN = 2

class Fidelity(Enum):
    LOW_RESOLUTION = 0
    HIGH_RESOLUTION = 1

class Mesh(object):
    def __init__(self, mesh_type, points):
        self.mesh_type = mesh_type
        self.points = points

class Xml(object):
    def __init__(self, fidelity, van_mises_mesh, displacement_mesh, strain_mesh):
        self.fidelity = fidelity
        self.van_mises_mesh = van_mises_mesh
        self.displacement_mesh = displacement_mesh
        self.strain_mesh = strain_mesh

# to access something inside a class, example strain_mesh points, you do
# xml.strain_mesh.points

class Sample(object):
    def __init__(self, low_resolution, high_resolution):
        self.low_resolution = low_resolution  # low-resolution xml
        self.high_resolution = high_resolution  # high-resolution xml

#"Low Resolution 3440"
#"Read VTU file"
#file_name_LR = "C:/Users/ra56niq/Documents/aneurysm_data/coarse/karlheinz_coarse_beta_rf_125_group_0__run_0-files/structure-0-0.vtu"

#"High Resolution 84889"
#file_name_HR = "C:/Users/ra56niq/Documents/aneurysm_data/fine/processedkarlheinz_fine_beta_rf_125_group_0__run_0-files/structure-0-0.vtu"


DATA_ROOT = r"/Users/nadavnagel/Desktop/Thesis/data" ##aneurysm_data
batch_namber = 43
FINE_FOLDER_NAME = 'fine'
COARSE_FOLDER_NAME = 'coarse'

# VTU_FILENAME = 'structure-0-0.vtu'
# PICKLE_FILENAME = '43_samples.pickle'
PICKLE_FILEPATH = DATA_ROOT


def read_from_xml(file_path, fidelity):
    """Read VTU file"""

    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(file_path)
    reader.Update()  # Needed because of GetScalarRange
    output = reader.GetOutput()
    # Saving into Numpy arrays
   # print(output.GetPointData())
    displacement = Mesh(
            MeshType.DISPLACEMENT,
            vtk_to_numpy(output.GetPointData().GetArray("displacement")))
    try:
        strain = Mesh(
                MeshType.STRAIN,
                vtk_to_numpy(output.GetPointData().GetArray("nodal_EA_strains_xyz")))
    except:
        strain_a = vtk_to_numpy(output.GetPointData().GetArray("nodal_EA_strains_eigenval1"))
        strain_b = vtk_to_numpy(output.GetPointData().GetArray("nodal_EA_strains_eigenval2"))
        strain_c = vtk_to_numpy(output.GetPointData().GetArray("nodal_EA_strains_eigenval3"))
        strain_a = np.reshape(strain_a, (np.shape(strain_a)[0], 1))
        strain_b = np.reshape(strain_b, (np.shape(strain_b)[0], 1))
        strain_c = np.reshape(strain_c, (np.shape(strain_c)[0], 1))
        strain = np.concatenate((strain_a, strain_b, strain_c), axis=1)
        strain = Mesh(MeshType.STRAIN, strain)
    van_mises = Mesh(
            MeshType.VAN_MISES,
            vtk_to_numpy(output.GetPointData().GetArray("nodal_cauchy_stresses_xyz")))
    return Xml(fidelity, van_mises, displacement, strain)


def get_sample_number(file):
    return int(file.split('_')[-3]), int(file.split('_')[-2])


def get_files_with_number(type='coarse'):
    if type == 'coarse':
        identify = 'lofi'
    else:
        identify = 'hifi'
    dic = {}
    root = os.path.join(DATA_ROOT, type)
    folders = sorted(os.listdir(root))
    folders = [i for i in folders if identify in i]
    for folder in folders:
        files = sorted(os.listdir(os.path.join(root, folder)))
        files = [i for i in files if '.vtu' in i]
        for file in files:
            dic[get_sample_number(file)] = os.path.join(root, folder, file)
    return dic


def get_max_obs(coarse_samples_path, fine_samples_path):
    indexes = []
    for i in coarse_samples_path.keys():
        indexes.append(i[1])
    for i in fine_samples_path.keys():
        indexes.append(i[1])
    return max(indexes)


def load_all_samples():
    coarse_samples_path = get_files_with_number(type='coarse')
    fine_samples_path = get_files_with_number(type='fine')
    last_obs = get_max_obs(coarse_samples_path, fine_samples_path)
    samples = []
    counter = 1
    for i in range(0, last_obs): ## last_obs
        sample_number = (batch_namber, i)
        if sample_number in coarse_samples_path:
            if sample_number in fine_samples_path:
                print('reading index:', sample_number)
                coarse_xml = read_from_xml(
                        coarse_samples_path[sample_number],
                        Fidelity.LOW_RESOLUTION)
                fine_xml = read_from_xml(
                        fine_samples_path[sample_number],
                        Fidelity.HIGH_RESOLUTION)
                samples.append(Sample(coarse_xml, fine_xml))
                if counter % 100 == 0:
                    pickle_name = 'batch{}_obs{}_{}.pickle'.format(batch_namber, counter-100, counter-1)
                    save_pickle(samples, pickle_name)
                    print('-'*80, '\n', PICKLE_FILEPATH, '/', pickle_name, ' -- saved\n', '-'*80)
                    samples = []
                print('opened total obs:', counter)
                counter += 1
    if counter+1 % 100 != 0:
        pickle_name = 'batch{}_obs{}_{}.pickle'.format(batch_namber, counter - 200, counter-1)
        save_pickle(samples, pickle_name)


def save_pickle(samples,PICKLE_FILENAME):
    with open(os.path.join(PICKLE_FILEPATH, PICKLE_FILENAME), 'wb') as fout:
        pickle.dump(samples, fout)


def read_pickle(PICKLE_FILENAME):
    with open(os.path.join(PICKLE_FILEPATH, PICKLE_FILENAME), 'rb') as fin:
        return pickle.load(fin)


if __name__ == '__main__':
    load_all_samples()


