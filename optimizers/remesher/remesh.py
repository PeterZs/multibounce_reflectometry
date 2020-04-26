import pstereo
import integrate
import z2mesh
import plyutils
import math
import sys

from matplotlib import pyplot as plt
import numpy as np

def remesh(meshfile, omeshfile, keep_normals=False, integrator=integrate.integrate, invert_normals=True, edge_protect=0):
    # Load pre-defined normals from a CSV (exported from MATLAB).
    # Use pstereo.get_normals(images, lights) to obtain normals using photometric
    # stereo.
    (vertices, normals, indices) = plyutils.readPLY(meshfile)

    # normalize the normals.
    albedos = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = normals / albedos

    old_normals = np.array(normals)
    #print(old_normals[2000:2020,:])
    #print("OLD: ", old_normals[0, :], " keep_normals: ", keep_normals)

    #print(normals.shape)
    w = int(math.sqrt(normals.shape[0]))
    h = w
    normals = normals.reshape((w,h,3))

    if invert_normals:
        normals[:, :, 2] = -normals[:, :, 2]

    if np.sum(normals[:,:,2]) > 0:
        zflipped = False
    else:
        zflipped = True
    # Integrate normals into a heightfield.
    zfield = integrator(normals, zflipped=zflipped, edge_protect=edge_protect)

    # Some stats.
    print("zmax: ", np.max(zfield))
    print("zmin: ", np.min(zfield))
    #print(normals[30:32,30:32,:])

    # Create a mesh from the heightfield.
    mesh = z2mesh.z2mesh(zfield, -1.0, 1.0, -1.0, 1.0, flip=False)

    # Expand mesh components.
    new_vertices, new_normals, new_indices = mesh

    if keep_normals:
        #old_normals[:, :, 2] = -old_normals[:, :, 2]
        #old_normals[:, 2] = -old_normals[:, 2]
        new_normals = old_normals * albedos

    #print("NEW: ", new_normals[0, :])
    # Write the mesh to mesh file.
    plyutils.writePLY(omeshfile, new_vertices, -new_normals, new_indices)