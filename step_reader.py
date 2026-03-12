import trimesh

def extract_step_dimensions(file_path):

    try:
        mesh = trimesh.load(file_path, force='mesh')

        bounds = mesh.bounds

        xmin, ymin, zmin = bounds[0]
        xmax, ymax, zmax = bounds[1]

        length = xmax - xmin
        width = ymax - ymin
        thickness = zmax - zmin

        volume = mesh.volume

        return length, width, thickness, volume

    except Exception as e:
        raise Exception("STEP file could not be processed. Please enter dimensions manually.")
