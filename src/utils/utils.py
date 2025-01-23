import os

def directory_to_list(dir):
    ext = (".png", ".jpg", ".jpeg")

    d = os.listdir(dir)
    source_list = [os.path.join(dir, f) for f in d if os.path.splitext(f)[1] in ext]

    return source_list


def validate_source(source):
    # convert source format into standard list of file paths
    if isinstance(source, list):
        source_list = [f for f in source if os.path.isfile(f)]
    elif os.path.isdir(source):
        source_list = directory_to_list(source)
    elif os.path.isfile(source):
        source_list = [source]
    else:
        raise ValueError('"source" expected as file, list or directory.')

    return source_list