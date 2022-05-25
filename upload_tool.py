import pysftp
import random
import os

load_dotenv()

def recursive_upload(server, local, remote, preserve_mtime=False):
    for name in os.listdir(local):
        rpath = remote + "/" + name
        lpath = os.path.join(local, name)

        if not os.path.isfile(lpath):
            try:
                server.mkdir(rpath)

            except OSError:     
                pass
            recursive_upload(server, lpath, rpath, preserve_mtime)
        else:
            server.put(lpath, rpath, preserve_mtime=preserve_mtime)

def recursive_remove(server, rpath):
    file_list = server.listdir(rpath)
    for name in file_list:
        current_path = os.path.join(rpath, name)

        try:
            server.remove(current_path)
        except IOError:
            recursive_remove(server, current_path)

    server.rmdir(rpath)