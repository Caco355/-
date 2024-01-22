import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import subprocess
import threading
import csv
import pkg_resources
import logging



# 获取当前脚本所在的目录
current_directory = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
internal_folder = os.path.join(current_directory, "_internal")
dependencies_folder = os.path.join(internal_folder, "dependencies")


# 检查并创建"_interal"文件夹
_internal_folder = os.path.join(current_directory, "_internal")
if not os.path.exists(_internal_folder):
    os.makedirs(_internal_folder)
    logging.info(f"Created json folder at {_internal_folder}")

# 检查并创建"json"文件夹
json_folder = os.path.join(internal_folder, "json")
if not os.path.exists(json_folder):
    os.makedirs(json_folder)
    logging.info(f"Created json folder at {json_folder}")

# 检查并创建"result"文件夹
result_folder = os.path.join(internal_folder, "result")
if not os.path.exists(result_folder):
    os.makedirs(result_folder)
    logging.info(f"Created result folder at {result_folder}")

# 创建主窗口
root = tk.Tk()
root.title("输入信息界面")
root.geometry("1000x600")  # 设置窗口大小为 1000x600 像素

# 创建左侧框架
left_frame = tk.Frame(root)
left_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

# 创建文本框用于输入多个公众号名称
label_gzh = tk.Label(left_frame, text="请输入多个公众号名称，用逗号分隔:", anchor="w")
label_gzh.pack(fill="both")

text_gzh = tk.Text(left_frame, height=4, width=50)
text_gzh.pack()

# 创建文本框用于输入多个关键词
label_keyword = tk.Label(left_frame, text="请输入多个关键词，用逗号分隔:", anchor="w")
label_keyword.pack(fill="both")

text_keyword = tk.Text(left_frame, height=4, width=50)
text_keyword.pack()

# 创建显示框用于显示输入的名称和关键词
display_label = tk.Label(left_frame, text="您输入的公众号名称和关键词:", anchor="w")
display_label.pack(fill="both")

display_text = tk.Text(left_frame, height=6, width=60)
display_text.pack()

# 创建文本框用于显示 de.py 运行过程
output_label = tk.Label(left_frame, text="运行过程:", anchor="w")
output_label.pack(fill="both")

output_text = tk.Text(left_frame, height=20, width=60)
output_text.pack()

# 创建开始按钮，用于保存输入的多个名称和关键词并运行 de.py 文件
def run_de_py():
    def run_de_thread():

        # 构建结果文件夹、JSON文件夹和最终文件夹的完整路径
        result_folder = os.path.join(current_directory, "result")
        json_folder = os.path.join(current_directory, "json")
        final_folder = os.path.join(current_directory, "final")

        # 创建结果、JSON和最终文件夹，如果它们不存在
        if not os.path.exists(result_folder):
            os.makedirs(result_folder)
        if not os.path.exists(json_folder):
            os.makedirs(json_folder)
        if not os.path.exists(final_folder):
            os.makedirs(final_folder)

        # 在点击开始按钮时删除json和result文件夹内的所有文件
        if os.path.exists(json_folder):
            for filename in os.listdir(json_folder):
                file_path = os.path.join(json_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        if os.path.exists(result_folder):
            for filename in os.listdir(result_folder):
                file_path = os.path.join(result_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        gzh_names = text_gzh.get("1.0", "end-1c").split(",")  # 获取输入的多个公众号名称
        keywords = text_keyword.get("1.0", "end-1c").split(",")  # 获取输入的多个关键词

        # 保存到 weinames.xlsx
        weinames_data = pd.DataFrame({'公众号名称': gzh_names})
        weinames_xlsx = os.path.join(current_directory, "weinames.xlsx")
        with pd.ExcelWriter(weinames_xlsx, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            weinames_data.to_excel(writer, index=False, sheet_name='Sheet1')

        # 保存到 12333.xlsx
        data = pd.DataFrame({'forbid': keywords})
        excel_12333 = os.path.join(current_directory, "12333.xlsx")
        with pd.ExcelWriter(excel_12333, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            data.to_excel(writer, index=False, sheet_name='Sheet1')

        # 在显示框中显示输入的名称和关键词
        display_text.delete("1.0", "end")
        display_text.insert("1.0", "您输入的公众号名称：\n")
        display_text.insert("end", "\n".join(gzh_names))
        display_text.insert("end", "\n\n您输入的关键词：\n")
        display_text.insert("end", "\n".join(keywords))

        # 运行外部的 de.py 文件并将输出实时显示
        process = subprocess.Popen(["python", "de.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            output_line = process.stdout.readline()
            if output_line == "" and process.poll() is not None:
                break
            output_text.insert("end", output_line)
            output_text.see("end")
            root.update_idletasks()

        # 运行完成后弹出通知窗口
        messagebox.showinfo("运行完成", "de.py 运行完成")

    # 使用线程以防止界面冻结
    threading.Thread(target=run_de_thread).start()

# 创建开始按钮，用于保存输入的多个名称和关键词并运行 de.py 文件
start_button = tk.Button(left_frame, text="开始", command=run_de_py)
start_button.pack()

# 创建右侧框架
right_frame = tk.Frame(root)
right_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)

# 创建文本框用于显示查看结果中选择的 CSV 文件内容
csv_label = tk.Label(right_frame, text="查看选择的 CSV 文件内容:", anchor="w")
csv_label.pack(fill="both")

# 创建文本框用于显示查看结果中选择的 CSV 文件内容
csv_display_text = tk.Text(right_frame, height=40, width=100)
csv_display_text.pack()

# 在显示 CSV 内容时，按照指定的格式排列标题和匹配的项
def display_csv_contents():
    try:
        # 使用 pkg_resources 来获取可执行文件的资源路径
        exe_path = pkg_resources.resource_filename(__name__, "")

        # 构建 final 文件夹的完整路径
        final_folder = os.path.join(current_directory, "final")

        # 使用 filedialog 来选择要查看的 CSV 文件
        file_path = filedialog.askopenfilename(initialdir=final_folder, title="选择要查看的 CSV 文件", filetypes=[("CSV 文件", "*.csv")])
        if file_path:
            csv_display_text.delete("1.0", "end")
            with open(file_path, "r", encoding="utf-8") as csv_file:
                # 读取所有行并将它们存储在一个列表中
                lines = csv_file.readlines()
                if len(lines) == 1 and not lines[0].strip():  # 如果文件只包含一个空白行，即标题行为空
                    csv_display_text.insert("end", "CSV 文件为空")  # 输出CSV文件为空的消息
                else:
                    for line in lines:
                        elements = line.strip().split(",")  # 尝试以逗号分隔
                        if len(elements) >= 2:  # 确保至少有标题和匹配的项两列
                            title = elements[0].strip('"')  # 去掉标题中的双引号
                            match_item = elements[1].strip('"')  # 去掉匹配的项中的双引号
                            formatted_line = f'文章《{title}》\t包含不合规字符：{match_item}\n\n'
                            csv_display_text.insert("end", formatted_line)
                        else:
                            csv_display_text.insert("end", f"无效行: {line}\n")  # 显示具体的无效行
        else:
            csv_display_text.delete("1.0", "end")  # 清空文本框内容
            csv_display_text.insert("end", "未选择 CSV 文件")  # 输出未选择CSV文件的消息
    except Exception as e:
        messagebox.showerror("错误", f"无法打开文件: {str(e)}")


view_csv_button = tk.Button(right_frame, text="查看结果", command=display_csv_contents)
view_csv_button.pack()

# 启动主循环
root.mainloop()
