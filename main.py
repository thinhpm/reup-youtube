import os
import requests
import numpy as np
import time
import subprocess
import json

np.seterr(over='ignore')
key_api = "AIzaSyAdO-hmFHLaRgiARrMRNdpN9RqgYx_ulB4"

pwd = os.getcwd()
pwd = pwd + '/'


def check_exist_chapt(id_series, id_chapt_new, stt_id):
    name_file = stt_id + "/save-data.txt"

    fo = open(name_file, "r")

    lines = fo.readlines()
    # format series:chapt,chapt\n
    for line in lines:
        arr_split = line.split(':')
        if (len(arr_split) > 1):
            series_current = arr_split[0]
            list_chapt_current = arr_split[1].replace('\n', '').split(',')

            if (str(series_current) == str(id_series)):
                if str(id_chapt_new) in list_chapt_current:
                    return False
    fo.close()
    return True


def save_to_file(id_series, id_chapt_new, stt_id):
    name_file = stt_id + "/save-data.txt"

    fo = open(name_file, "r")
    lines = fo.readlines()
    check = True
    i = 0
    len_lines = len(lines)
    n = '\n'
    # format series:chapt,chapt\n
    for line in lines:
        arr_split = line.split(':')
        if (len(arr_split) > 1):
            series_current = arr_split[0]
            list_chapt_current = arr_split[1].replace('\n', '')

            if (i == len_lines - 1):
                n = ''
            if (str(series_current) == str(id_series)):
                list_chapt_current = str(id_series) + ':' + str(list_chapt_current) + ',' + str(id_chapt_new) + n
                lines[i] = list_chapt_current
                check = False
        i = i + 1
    if (check):
        if (len(lines) > 0):
            lines[len(lines) - 1] = lines[len(lines) - 1] + '\n'
        lines.append(str(id_series) + ':' + id_chapt_new)
    fo.close()

    fo = open(name_file, "w")
    fo.writelines(lines)
    fo.close()
    return True


def upload_youtube_and_check_out_number(title, description, tags, file_name, stt_id):
    #'--thumbnail=' + thumbnail,
    process = subprocess.Popen(['py', 'youtube-upload', '--title=' + str(title) + '', '--tags=' + tags,
                                '--description=' + description, '--client-secrets=' + stt_id + '/client_secrets.json',
                                '--credentials-file=' + stt_id + '/credentials.json', file_name],
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    print(stdout)
    # return 'Video URL' in stdout
    return True


def isFirstUpload(stt_id):
    f = open(stt_id + '/credentials.json', 'r')
    lines = f.readlines()
    f.close()
    if(len(lines) == 0):
        return True

    return False


def get_file_upload():
    filelist = os.listdir('input')

    for fichier in filelist:
        if "input" in fichier:
            return fichier

    return False


def get_ffmpeg(file_video, file_ffmpeg):
    path_file = 'ffmpeg-files/' + file_ffmpeg
    fo = open(path_file, "r")
    lines = fo.readlines()

    if len(lines) > 0:
        string_process = lines[0]
        string_process = string_process.replace("input.mp4", 'input/' + str(file_video))
        string_process = string_process.replace("output.mp4", "output/" + str(file_video))

        return string_process

    return False


def process_video(file_name):
    string_ffmpeg = get_ffmpeg(file_name, 'text2.txt')
    os.system(string_ffmpeg)

    return 'output/' + file_name


def hanlde(name_title, description, genres, stt_id):
    check = False
    file_name = get_file_upload()
    temp_file_name = file_name
    file_name = process_video(file_name)

    if file_name:
        print("Uploading...")

        if isFirstUpload(stt_id):
            print('youtube-upload --title="' + str(
                name_title) + '" --description="' + description + '" --tags="' + genres + '" ' + ' --client-secrets="' +
                      stt_id + '/client_secrets.json" --credentials-file="' + stt_id + '/credentials.json" ' + file_name)
            os.system('py youtube-upload --title="' + str(
                name_title) + '" --description="' + description + '" --tags="' + genres + '" ' + ' --client-secrets="' +
                      stt_id + '/client_secrets.json" --credentials-file="' + stt_id + '/credentials.json" ' + file_name)

            check = True
        else:
            check = upload_youtube_and_check_out_number(name_title, description, genres, file_name, stt_id)

    os.remove('input/' + temp_file_name)
    os.remove('output/' + temp_file_name)

    return check


def download_video_from_youtube(id_video):
    print("Downloading...")
    url = "youtube-dl -o input/input.%(ext)s https://www.youtube.com/watch?v=" + str(id_video)
    os.system(url)


def get_tags(id_video):
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&key=" + key_api + "&id=" + str(id_video)

    req = requests.get(url)
    items = json.loads(req.content)

    list_tag = ','.join(items['items'][0]['snippet']['tags'])

    return list_tag


def get_list_video(channel_id, stt_id):
    print("Get list video..")
    max_result = 50

    url = "https://www.googleapis.com/youtube/v3/activities?part=snippet,contentDetails&key=" \
          + str(key_api) + "&channelId=" + str(channel_id) + "&maxResults=" + str(max_result)

    req = requests.get(url)

    list_item = json.loads(req.content)

    for item in list_item['items']:
        title = item['snippet']['title']
        description = title

        id_video = item['contentDetails']['upload']['videoId']

        if check_exist_chapt(channel_id, id_video, stt_id):
            tags = get_tags(id_video)
            download_video_from_youtube(id_video)

            check = hanlde(title, description, tags, stt_id)

            if check:
                save_to_file(channel_id, id_video, stt_id)
                print("Done")
                time.sleep(150)


def get_source_links(stt_id):
    # read file get arr website avail
    fo = open(stt_id + "/source-links.txt", "r")
    arr_website_avail = []
    lines = fo.readlines()

    for line in lines:
        arr_website_avail.append(line.replace('\n', ''))
    fo.close()
    return arr_website_avail


if __name__ == '__main__':
    stt_id = str(input("Enter id: "))
    arr_website_avail = get_source_links(stt_id)

    for item_web in arr_website_avail:
        get_list_video(item_web, stt_id)
