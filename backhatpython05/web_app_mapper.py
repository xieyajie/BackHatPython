# encoding=utf-8

import queue
import threading
import os
import urllib

threads = 10

target = "http://www.blackhatpython.com"
directory = "/Users/xieyajie/Downloads/blackhatpython05"
filters = [".jpg", ".gif", ".png", ".css"]

# 改变目录到指定目录
os.chdir(directory)

web_paths = queue.Queue()

# 三元tupple(dirpath, dirnames, filenames)，其中第一个为起始路径，第二个为起始路径下的文件夹，第三个是起始路径下的文件。
for r, d, f in os.walk("."):
    for files in f:
        remote_path = "%s/%s" % (r, files)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        # os.path.splitext()分解路径: "c:\\123\\456\\test.txt"->["c:\\123\\456\\test", ".txt"]
        if os.path.splitext(files)[1] not in filter:
            web_paths.put(remote_path)

def test_remote():
    print("begin test")

    while not web_paths.empty():
        path = web_paths.get().decode()
        url = "%s%s" % (target, path)

        request = urllib.request.Request()

        try:
            response = urllib.request.urlopen(request)
            content = response.read()

            print("[%d] ==> %s" % (response.code, path))

            response.close()
        except urllib.request.HTTPError as error:
            pass

for i in range(threads):
    print("Spawning thread: %d" % i)

    t = threading.Thread(target=test_remote)
    t.start()



