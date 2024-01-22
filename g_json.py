import os
import json
import sys

if len(sys.argv) < 3:
    print("Usage: python g_json.py cookies_value user_agent fakeid token gzh_name")
    sys.exit(1)

cookies_value = sys.argv[1]
user_agent = sys.argv[2]
fakeid = sys.argv[3]
token = sys.argv[4]
gzh_name = sys.argv[5]

# 创建一个包含Cookie、User-Agent、FakeID、Token和gzh_name的示例字典
data = {
    "cookies": cookies_value,
    "user_agent": user_agent,
    "fakeid": fakeid,
    "token": token,
    "gzh_name": gzh_name,
}

# 创建保存 JSON 数据的文件夹（如果不存在）
json_folder = "json"
os.makedirs(json_folder, exist_ok=True)

# 拼接 JSON 文件的名称为 "data_fakeid.json"
file_name = os.path.join(json_folder, f"data_{fakeid}.json")

# 使用 'w' 模式打开文件，将数据写入 JSON 文件
with open(file_name, 'w') as json_file:
    json.dump(data, json_file, indent=4)  # indent 参数用于增加缩进，使 JSON 文件更可读

print(f"JSON 数据已保存到文件: {file_name}")
