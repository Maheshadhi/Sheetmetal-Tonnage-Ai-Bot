try:
    from OCC.Core.STEPControl import STEPControl_Reader
    from OCC.Core.Bnd import Bnd_Box
    from OCC.Core.BRepBndLib import brepbndlib_Add
    from OCC.Core.GProp import GProp_GProps
    from OCC.Core.BRepGProp import brepgprop_VolumeProperties
    OCC_AVAILABLE = True
except:
    OCC_AVAILABLE = False


def extract_step_dimensions(file_path):

    if not OCC_AVAILABLE:
        raise Exception("STEP processing not supported on this server")

    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(file_path)

    if status != 1:
        raise Exception("STEP file could not be read")

    step_reader.TransferRoots()
    shape = step_reader.Shape()

    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)

    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

    length = xmax - xmin
    width = ymax - ymin
    thickness = zmax - zmin

    props = GProp_GProps()
    brepgprop_VolumeProperties(shape, props)

    volume = props.Mass()

    return length, width, thickness, volume
