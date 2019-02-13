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


def analyse_file(root, path, name):
    result = os.stat(os.path.join(path, name), follow_symlinks=False)

    return {
        "file_name": name,
        "dirname": os.path.join(".", os.path.dirname(os.path.relpath(os.path.join(path, name), root))),
        "full_path": os.path.join(path, name),
        "file_type": file_type(result.st_mode),
        "file_size": result.st_size,
        "access_time": datetime.datetime.fromtimestamp(result.st_atime),
        "modification_time": datetime.datetime.fromtimestamp(result.st_mtime),
        "creation_time": datetime.datetime.fromtimestamp(result.st_ctime),
        "owner_id": result.st_uid,
        "group_id": result.st_gid,
    }


def walk(root, database, path_id_cache):
    database.begin()

    data = analyse_file(root, root, ".")
    parent_id = database.insert_file(data, None)
    path_id_cache["."] = parent_id

    for path, directories, files in os.walk(root):
        parent_id = path_id_cache[os.path.relpath(path, root)]

        for name in files:
            data = analyse_file(root, path, name)
            database.insert_file(data, parent_id)

        for name in directories:
            data = analyse_file(root, path, name)
            directory_id = database.insert_file(data, parent_id)

            path_id_cache[
                os.path.relpath(os.path.join(path, name), root)
            ] = directory_id

    database.commit()
    database.create_session()
