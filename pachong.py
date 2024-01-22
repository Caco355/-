import os
import json
import requests
import time
import random
import urllib3

# 禁用不安全请求的警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 获取json文件夹中所有的json文件列表
json_folder = "json"
json_files = [f for f in os.listdir(json_folder) if f.endswith(".json")]

# 遍历每个json文件并运行爬取代码
for json_file in json_files:
    file_path = os.path.join(json_folder, json_file)

    # 检查json文件是否存在
    if not os.path.exists(file_path):
        continue

    # 打开 JSON 文件并加载配置
    with open(file_path, "r", encoding='UTF-8') as file:
        config = json.load(file)

    headers = {
        "Cookie": config['cookies'],
        "User-Agent": config['user_agent'] 
    }

    url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
    params = {
        "action": "list_ex",
        "begin": "0",
        "count": "5",
        "fakeid": config['fakeid'],
        "type": "9",
        "token": config['token'],
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1"
    }

    i = 0
    while True:
        try:
            params["begin"] = str(i * 5)
            time.sleep(random.randint(1, 10))
            resp = requests.get(url, headers=headers, params=params, verify=False)

            if resp.status_code != 200:
                print(f"请求失败，状态码：{resp.status_code}")
                break

            data = resp.json()
            if 'base_resp' in data and data['base_resp']['ret'] == 200013:
                print("频率控制，暂停一小时")
                time.sleep(3600)
                continue

            if 'app_msg_list' in data and len(data['app_msg_list']) == 0:
                print("所有文章已爬取")
                break

            for item in data.get("app_msg_list", []):
                gzh_name = config['gzh_name']
                result_folder = "result"  # 结果文件夹名称
                file_name = os.path.join(result_folder, f"app_msg_list_{gzh_name}.csv")  # 修改文件路径

                info = '"{}","{}","{}","{}"'.format(str(item["aid"]), item['title'], item['link'], str(item['create_time']))

                if i == 0:
                    with open(file_name, "w", encoding='utf-8-sig') as f:
                        f.write("文章标识符aid,标题title,链接url,时间time\n")

                with open(file_name, "a", encoding='utf-8-sig') as f:
                    f.write(info + '\n')
                print(f"第{i}页爬取成功，保存为 {file_name}")
            i += 1

        except Exception as e:
            print(f"发生异常: {e}")
            break
