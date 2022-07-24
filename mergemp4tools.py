# coding=gbk
import os


def Merge(filename):
    """
    将音频视频合并成mp4
    :return:
    """
    audio = 'testaudio.m4s'
    video = 'testvideo.m4s'
    cmand = "ffmpeg -i " + '"' + video + '"' + " -i " + '"' + audio + '"' + " -c:v copy -strict experimental "
    name2 = filename
    cmand = cmand + name2
    os.system(cmand)


if __name__ == '__main__':
    Merge('自定义文件.mp4')
