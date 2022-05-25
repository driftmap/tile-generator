import pysftp
import random
import os

def recursive_upload(server, local, remote) -> None:
    for name in os.listdir(local):
        rpath = remote + "/" + name
        lpath = os.path.join(local, name)

        if not os.path.isfile(lpath):
            try:
                server.mkdir(rpath)

            except OSError:     
                pass
            recursive_upload(server, lpath, rpath)
        else:
            server.put(lpath, rpath)

def recursive_remove(server, rpath) -> None:
    file_list = server.listdir(rpath)
    for name in file_list:
        current_path = os.path.join(rpath, name)

        try:
            server.remove(current_path)
        except IOError:
            recursive_remove(server, current_path)

    server.rmdir(rpath)

def upload_all(HOSTNAME, USERNAME, DRIFT_KEY, LOCAL_DIR):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    srv = pysftp.Connection(host=HOSTNAME, username=USERNAME, password=DRIFT_KEY, log="pysftp.log", cnopts=cnopts)

    new_folder = "tiles" + str(random.randrange(1,100))
    srv.mkdir(new_folder, mode=774)

    with srv.cd(new_folder):
        current_dir = srv.pwd
        #print(srv.pwd)
        local_dir = LOCAL_DIR
        recursive_upload(srv, local_dir, current_dir) 

    old_tiles = "tiles"
    with srv.cd(old_tiles):
        current_dir = srv.pwd
        #print(current_dir)
        recursive_remove(srv, current_dir)

    current_dir = srv.pwd
    srv.close()