# Box Crawler
Easily download all the videos and PDF files from tus.app.box.com.

## Environment

* Python 3.7 and above are recommended

* Anaconda is recommended

* This project uses [FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases) and requests. Go check them out if you don't have them locally installed.

```sh
$ requests
pip install requests
```

## Usage

1. Log in your Tus box account. Open any video that needs to be downloaded.

2. Switch to the developer tool. `F12` → `Network` → `Ctrl R`

3. Pick the first label like below.

![image-20220724160135954](D:\PyCharmProject\Box_Crawler\img\image-20220724160135954.png)



4. Select `cookies` and copy the value. Replace the value of `cookies` in the configuration file.

![image-20220724160242840](D:\PyCharmProject\Box_Crawler\img\image-20220724160242840.png)



5. Drag the video progress bar to the end.

![image-20220724160634625](D:\PyCharmProject\Box_Crawler\img\image-20220724160634625.png)



6. Check the developer tool to get the serial number of the end clip of the video.

![image-20220724160851203](D:\PyCharmProject\Box_Crawler\img\image-20220724160851203.png)



7. Replace the value of `end` in the configuration file. (An one-hour-long video usually has 700 clips.)

![image-20220724160937591](D:\PyCharmProject\Box_Crawler\img\image-20220724160937591.png)

8. Execute the program.

```shell
cd Box_Crawler
python crawl.py
```



## Additional information

* Some videos do not have 1080p picture quality. You need to change the `quality` parameter of the configure to 480 before executing.

* When downloading PDF files, you only need to change the parameter of ` cookie`.
