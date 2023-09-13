import os
import numpy as np

from ase.spacegroup.symmetrize import FixSymmetry
from ase.io import read, write

from matlantis_features.features.common.opt import LBFGSASEOptFeature

os.environ["MATLANTIS_PFP_MODEL_VERSION"] = "v4.0.0"
os.environ["MATLANTIS_PFP_CALC_MODE"] = "crystal_u0"

# ---------- input structure
# CrySPY outputs 'POSCAR' as an input file in work/xxxxxx directory
atoms = read('POSCAR', format='vasp')

# ---------- setting and run    
def filter_structure(atoms_cell):
    n = np.cross(atoms_cell[0], atoms_cell[1])
    c = atoms_cell[2]
    # Calculate the dot product between c and n
    dot_product = np.dot(c, n)

    # Calculate the magnitudes of c and n
    mag_c = np.linalg.norm(c)
    mag_n = np.linalg.norm(n)

    # Calculate the cosine of the angle theta
    cos_theta = dot_product / (mag_c * mag_n)

    # Calculate the angle theta in radians
    theta_rad = np.arccos(np.clip(cos_theta, -1, 1))

    # Convert theta from radians to degrees if needed
    theta_deg = np.degrees(theta_rad)

    # print("Theta (in degrees):", np.abs(90 - theta_deg))

    if np.abs(90 - theta_deg) > 25.0:
        return True
    else:
        return False

if filter_structure(atoms.cell):
    atoms.set_constraint([FixSymmetry(atoms)])
    opt = LBFGSASEOptFeature(n_run=10000, filter=True)
    result_opt = opt(atoms)
    e = result_opt.atoms.ase_atoms.get_total_energy()
    with open('log.tote', mode='w') as f:
        f.write(str(e))

    write('CONTCAR', result_opt.atoms.ase_atoms, format='vasp')

else:
    with open('log.tote', mode='w') as f:
        f.write(str(0.00))

    write('CONTCAR', atoms, format='vasp')