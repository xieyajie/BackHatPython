# coding = utf-8

import urllib
import urllib.parse
import urllib.request
import threading
import queue

threads = 5
target_url = "http://testphp.vulnweb.com"
wordlist_file = "./tmp/all.txt"
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
word_queue = None

def build_wordlist(wordlist_file):
    global  resume

    fd = open(wordlist_file, "rb")
    raw_words = fd.readlines()
    fd.close()

    found_resume = False
    words = queue.Queue()

    for word in raw_words:
        #rstrip() 删除 string 字符串末尾的指定字符（默认为空格）
        word = word.decode().rstrip()

        if resume is None:
            resume = word

        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print("Resuming wordlist from %s" % resume)
    else:
        words.put(word)

    return words


def dir_bruter(extensions=None):

    while not word_queue.empty():
        attempt = word_queue.get()
        attempt_list = []

        if "." not in attempt:
            attempt_list.append("/%s/" % attempt)
        else:
            attempt_list.append("/%s" % attempt)

        if extensions:
            for extension in extensions:
                attempt_list.append("/%s%s" % (attempt, extension))

        for brute in attempt_list:
            # quote() 将url中的特殊字符或汉字encode成指定编码, 比如如果url里面的空格
            url = "%s%s" % (target_url, urllib.parse.quote(brute))

            try:
                headers = {}
                headers["User-Agent"] = user_agent
                r = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(r)

                if len(response.read()):
                    print("[%d]==> %s" % (response.code, url))

            except urllib.request.HTTPError as e:
                print("Failed [%d]==> %s" % (e.code, url))
                resume = attempt

                if e.code != 404:
                    print("!!! %d => %s" % (e.code, url))
                pass


word_queue = build_wordlist(wordlist_file)
extensions = [".php",".bak",".orig",".inc"]

for i in range(threads):
    t = threading.Thread(target=dir_bruter, args=(extensions,))
    t.start()




