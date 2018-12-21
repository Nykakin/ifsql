import datetime
import stat
import os
import os.path


def file_type(mode):
    if stat.S_ISDIR(mode):
        return "D"
    if stat.S_ISREG(mode):
        return "F"
    if stat.S_ISCHR(mode):
        return "C"
    if stat.S_ISBLK(mode):
        return "B"
    if stat.S_ISFIFO(mode):
        return "N"
    if stat.S_ISLNK(mode):
        return "L"
    if stat.S_ISSOCK(mode):
        return "S"


def analyse_file(path, name):
    result = os.stat(os.path.join(path, name))

    return {
        "file_name": name,
        "file_path": path,
        "file_type": file_type(result.st_mode),
        "file_size": result.st_size,
        "access_time": datetime.datetime.fromtimestamp(result.st_atime),
        "modification_time": datetime.datetime.fromtimestamp(result.st_mtime),
        "owner_id": result.st_uid,
        "group_id": result.st_gid,
    }


def walk(root, database, path_id_cache):
    parent_node = None
    for root, _, files in os.walk(root):
        if parent_node is None:
            data = analyse_file(root, ".")
            parent_node = database.insert_file(data, None)
            path_id_cache["."] = parent_node.file_id
        else:
            data = analyse_file(os.path.dirname(root), os.path.basename(root))
            parent_node = database.insert_file(data, parent_node)
            path_id_cache[root] = parent_node.file_id

        for name in files:
            data = analyse_file(root, name)
            database.insert_file(data, parent_node)
