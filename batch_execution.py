import configparser
import os

a = "https://tus.app.box.com/s/3kdltc9knis80tm5z5ood43ikxlm7ne5"
b = "https://tus.app.box.com/s/prtq4kyk59u6rqjp8sar7v2pvxdsi71k"
c = "https://tus.app.box.com/s/m7hd1hqq4zn3ihtuqompmp7f8e0bdm7o"
# d = "https://tus.app.box.com/s/0ndd4ph7zwna4wa1t50ae8xlru0fs4dx"
# e = "https://tus.app.box.com/s/5q5d8nbevxby0ixkpyyon64wgfxkwk4i"

a1 = "445"
b1 = "351"
c1 = "228"
# d1 = "140"
# e1 = "44"


def change_url_end(url, end):
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    config.set("base", "url", url)
    config.set("mp4conf", "end", end)
    config.write(open("config.ini", "w"))
    # r = config.get("base", "url")
    # print("url = "+r)
    # print("开始爬取录像")


def change_quality(quality):
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    config.set("base", "quality", quality)
    config.write(open("config.ini", "w"))


def main():
    url_list = [a, b, c]
    end_list = [a1, b1, c1]
    pair = list(zip(url_list, end_list))
    quality = "1080"
    change_quality(quality)
    for url, end in pair:
        change_url_end(url, end)
        print(url, end)
        os.system("python crawl.py")


if __name__ == '__main__':
    main()
