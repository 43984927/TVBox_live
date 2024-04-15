import requests
from lxml import etree
import os
import threading
import time
import sys


# def get_url(name):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
#     }
#     url = "http://tonkiang.us/"
#     # 获取两页的m3u8链接
#     # params = {
#     #     "page": 1,
#     #     "s": name
#     # }
#     # response = requests.get(url, headers=headers, params=params, verify=False)
#     data = {
#         "search": name,
#         "Submit": " "
#     }
#     try:
#         time.sleep(5)
#         with requests.Session() as session:
#             response = session.post(url, headers=headers, data=data, verify=False)
#             print(response)
#         # print(response.text)
#         # 将 HTML 转换为 Element 对象
#         root = etree.HTML(response.text)
#         result_divs = root.xpath("//div[@class='result']")
#
#         # 打印提取到的 <div class="result"> 标签
#         m3u8_list = []
#         for div in result_divs:
#             # 如果要获取标签内的文本内容
#             # print(etree.tostring(div, pretty_print=True).decode())
#             for element in div.xpath(".//tba"):
#                 if element.text is not None:
#                     m3u8_list.append(element.text.strip())
#                     print(element.text.strip())
#         return m3u8_list
#
#     except requests.exceptions.RequestException as e:
#         print(f"Error: 请求异常. Exception: {e}")
#         return
def get_url(name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    url = "http://tonkiang.us/"
    data = {
        "search": f"{name}",
        "Submit": " "
    }
    try:
        res = requests.get(url, headers=headers, data=data, verify=False)
        cookie = res.cookies

        for i in range(5):
            url = f"http://tonkiang.us/?page={i + 1}&s={name}"
            time.sleep(10)
            response = requests.get(url, headers=headers, cookies=cookie, verify=False)
            root = etree.HTML(response.text)
            result_divs = root.xpath("//div[@class='result']")
            for div in result_divs:
                for element in div.xpath(".//tba"):
                    if element.text is not None:
                        yield element.text.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error: 请求异常. Exception: {e}")
        return

def mer_links(tv):
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

if __name__ == '__main__':


def re_dup(filepath):
    from collections import OrderedDict
    # 读取文本文件
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # 保持原始顺序的去重
    unique_lines_ordered = list(OrderedDict.fromkeys(lines))
    # 将去重后的内容写回文件
    with open(filepath, 'w', encoding='utf-8') as file:
        file.writelines(unique_lines_ordered)
    print('-----直播源去重完成！------')


if __name__ == '__main__':
    print('说明：\n'
          '速度阈值默认为1\n'
          '阈值越大，直播流速度越快，检索出的直播流数量越少\n'
          '建议日常阈值最小0.3，能够满足日常播放流不卡顿\n')
    # speed = input('请直接回车确定或输入阈值:  ')
    # if speed == '':
    #     speed = 1
    # else:
    #     speed = float(speed)
    speed = 0.5
    # 获取当前工作目录
    current_directory = os.getcwd()
    # 构造上级目录的路径
    parent_dir = os.path.dirname(current_directory)
    output_file_path = os.path.join(parent_dir, 'live.txt')
    # 清空live.txt内容
    with open(output_file_path, 'w', encoding='utf-8') as f:
        pass
    tv_dict = {}
    # 遍历当前文件下的txt文件,提取文件名
    TV_names = [os.path.splitext(f)[0] for f in os.listdir(current_directory) if f.endswith(".txt")]
    # '🇭🇰港台'  '🇨🇳卫视频道'  '🇨🇳央视频道'
    # TV_names = ['🇨🇳卫视频道']
    for TV_name in TV_names:
        # 删除历史测试记录，防止文件追加写入
        if os.path.exists(TV_name):
            import shutil
            # 删除文件夹及其内容
            try:
                shutil.rmtree(TV_name)
                print(f"Folder '{TV_name}' deleted successfully.")
            except OSError as e:
                print(f"Error deleting folder '{TV_name}': {e}")
        time.sleep(1)
        if not os.path.exists(TV_name):
            os.makedirs(TV_name)
        # 读取文件并逐行处理
        with open(f'{TV_name}.txt', 'r', encoding='utf-8') as file:
            names = [line.strip() for line in file]
            for name in names:
                m3u8_list = get_url(name)
                tv_dict[name] = m3u8_list
                print(name)
            print('---------字典加载完成！------------')
        for name, m3u8_list in tv_dict.items():
            detectLinks(name, m3u8_list)
        # 合并有效直播源m3u8链接
        mer_links(TV_name)
        tv_dict.clear()

    time.sleep(10)
    os.remove('video.ts')
    # 直播源去重
    re_dup(output_file_path)

    sys.exit()
