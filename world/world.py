import requests
from lxml import etree
import os
import threading
import time
import sys
from collections import OrderedDict
import shutil

speed = 0.5

def get_url(name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    url = "http://tonkiang.us/"
    data = {
        "search": name,
        "Submit": " "
    }

    try:
        res = requests.get(url, headers=headers, data=data, verify=False)
        cookie = res.cookies

        m3u8_list = []
        for i in range(5):
            url = f"http://tonkiang.us/?page={i + 1}&s={name}"
            time.sleep(10)
            response = requests.get(url, headers=headers, cookies=cookie, verify=False)
            root = etree.HTML(response.text)
            result_divs = root.xpath("//div[@class='result']")

            for div in result_divs:
                for element in div.xpath(".//tba"):
                    if element.text is not None:
                        m3u8_list.append(element.text.strip())
                        print(element.text.strip())

        return m3u8_list

    except requests.exceptions.RequestException as e:
        print(f"Error: 请求异常. Exception: {e}")
        return

def download_m3u8(url, name, initial_url=None):
    try:
        response = requests.get(url, stream=True, timeout=3)  # 设置超时时间为3秒
        response.raise_for_status()
        m3u8_content = response.text
    except requests.exceptions.Timeout as e:
        print(f"{url}\nError: 请求超时. Exception: {e}")
        return
    except requests.exceptions.RequestException as e:
        print(f"{url}\nError: 请求异常. Exception: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    lines = m3u8_content.split('\n')
    segments = [line.strip() for line in lines if line and not line.startswith('#')]

    if len(segments) == 1:
        return download_m3u8(segments[0], name, initial_url=initial_url if initial_url is not None else url)

    total_size = 0
    total_time = 0
    for i, segment in enumerate(segments[:3]):
        start_time = time.time()
        segment_url = url.rsplit('/', 1)[0] + '/' + segment
        response = requests.get(segment_url, timeout=3)  # 设置超时时间为3秒
        end_time = time.time()

        with open('video.ts', 'wb') as f:
            f.write(response.content)

        segment_size = len(response.content)
        segment_time = end_time - start_time
        segment_speed = segment_size / segment_time / (1024 * 1024)

        total_size += segment_size
        total_time += segment_time

        print(f"Downloaded segment {i + 1}/3: {segment_speed:.2f} MB/s")

        os.remove('video.ts')  # Delete the video segment file after speed test

    average_speed = total_size / total_time / (1024 * 1024)
    print(f"---{name}---Average Download Speed: {average_speed:.2f} MB/s")

    if average_speed >= speed:
        valid_url = initial_url if initial_url is not None else url
        if not os.path.exists(f'{name}'):
            os.makedirs(f'{name}')
        with open(os.path.join(f'{name}', f'{name}.txt'), 'a', encoding='utf-8') as file:
            file.write(f'{name},{valid_url}\n')
        print(f"---{name}---链接有效源已保存---\n"
              f"----{valid_url}---")
        return

def detectLinks(name, m3u8_list):
    thread = []
    for m3u8_url in m3u8_list:
        t = threading.Thread(target=download_m3u8, args=(m3u8_url, name,))
        t.daemon = True
        t.start()
        thread.append(t)

    for t in thread:
        try:
            print(f"Waiting for thread {t} to finish")
            t.join(timeout=10)
        except Exception as e:
            print(f"Thread {t.name} raised an exception: {e}")

def merge_links(tv):
    txt_files = [f for f in os.listdir(os.path.join(current_directory, f'{tv}'))]

    with open(output_file_path, 'a', encoding='utf-8') as output_file:
        output_file.write(f'{tv},#genre#' + '\n')
        for txt_file in txt_files:
            file_path = os.path.join(os.path.join(current_directory, f'{tv}'), txt_file)

            with open(file_path, 'r', encoding='utf-8') as input_file:
                for line in input_file:
                    output_file.write(line)

                output_file.write('\n')

    print(f'Merged content from {len(txt_files)} files into {output_file_path}')

def remove_duplicates(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    unique_lines_ordered = list(OrderedDict.fromkeys(lines))

    with open(filepath, 'w', encoding='utf-8') as file:
        file.writelines(unique_lines_ordered)

    print('-----直播源去重完成！------')

if __name__ == '__main__':
    current_directory = os.getcwd()
    parent_dir = os.path.dirname(current_directory)
    output_file_path = os.path.join(parent_dir, 'live.txt')

    with open(output_file_path, 'w', encoding='utf-8') as f:
        pass

    TV_names = [os.path.splitext(f)[0] for f in os.listdir(current_directory) if f.endswith(".txt")]

    for TV_name in TV_names:
        if os.path.exists(TV_name):
            try:
                shutil.rmtree(TV_name)
                print(f"Folder '{TV_name}' deleted successfully.")
            except OSError as e:
                print(f"Error deleting folder '{TV_name}': {e}")

        time.sleep(1)
        if not os.path.exists(TV_name):
            os.makedirs(TV_name)

        with open(f'{TV_name}.txt', 'r', encoding='utf-8') as file:
            for line in file:
                names = line.strip()
                m3u8_list = get_url(names)
                detectLinks(names, m3u8_list)

        merge_links(TV_name)

    time.sleep(10)

    remove_duplicates(output_file_path)

    sys.exit()
