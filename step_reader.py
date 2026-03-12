import trimesh

def extract_step_dimensions(file_path):

    mesh = trimesh.load(file_path)

    bounds = mesh.bounds

    xmin, ymin, zmin = bounds[0]
    xmax, ymax, zmax = bounds[1]

    length = xmax - xmin
    width = ymax - ymin
    thickness = zmax - zmin

    volume = mesh.volume

    return length, width, thickness, volume
    volume = props.Mass()

    return length, width, thickness, volume
