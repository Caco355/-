import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv

# 读取Excel文件
excel_data = pd.read_excel('12333.xlsx')  # 替换为您的Excel文件路径
# 假设您要比对的数据在某一列，例如名为'ColumnName'
excel_items = excel_data['forbid'].tolist()

# 获取result文件夹下的所有文件
result_folder = "result"
csv_files = [f for f in os.listdir(result_folder) if f.endswith(".csv")]

# 创建final文件夹，如果不存在的话
final_folder = "final"
os.makedirs(final_folder, exist_ok=True)

# 遍历每个CSV文件
for csv_file_name in csv_files:
    csv_file_path = os.path.join(result_folder, csv_file_name)

    # 打开输出CSV文件，使用final文件夹作为路径，并在文件名中加上"_matches"后缀
    output_csv_file_name = os.path.splitext(csv_file_name)[0] + "_matches.csv"
    output_csv_file_path = os.path.join(final_folder, output_csv_file_name)

    with open(output_csv_file_path, "w", newline='', encoding="utf-8-sig") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["标题", "匹配的项", "URL"])  # 写入CSV文件的标题行

        # 读取输入CSV文件
        with open(csv_file_path, "r", encoding="utf-8") as file:
            data = file.readlines()

        # 遍历CSV文件中的每一行
        for i, line in enumerate(data):
            if i == 0:  # 跳过CSV文件的标题行
                continue
            mes = line.strip().split(",")
            if len(mes) != 4:
                continue
            title, url = mes[1], mes[2].strip('"')  # 移除URL周围的引号

            try:
                # 检查URL格式
                if not url.startswith("http://") and not url.startswith("https://"):
                    print(f"无效的URL格式: {url}")
                    continue

                # 发送HTTP请求
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')

                    # 在网页文本中查找是否包含Excel表格中的任何项
                    web_text = soup.get_text()
                    for item in excel_items:
                        if item in web_text:
                            print(f"在网页 {url} 中找到了与Excel表格匹配的项：{item}")

                            # 将匹配的项和标题写入输出CSV文件
                            csv_writer.writerow([title, item, url])
                            break

            except requests.RequestException as e:
                print(f"请求 {url} 时出错: {e}")

    print(f"匹配的项和标题已写入到 {output_csv_file_name}，并保存到final文件夹内")
