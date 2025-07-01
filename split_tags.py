
import os
import tkinter as tk
from tkinter import filedialog

def split_tags_to_files(input_filepath, output_dir='output_tags', chunk_size=1000):
    """
    将tag列表文件拆分成每1000个一组，每组保存为一个txt文件。

    Args:
        input_filepath (str): 输入tag列表文件的路径。
        output_dir (str): 输出文件的目录。
        chunk_size (int): 每个文件的tag数量。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            tags = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"错误：文件未找到 - {input_filepath}")
        return
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        return

    file_count = 0
    for i in range(0, len(tags), chunk_size):
        file_count += 1
        chunk = tags[i:i + chunk_size]
        output_filename = os.path.join(output_dir, f'tags_part_{file_count:04d}.txt')
        with open(output_filename, 'w', encoding='utf-8') as f_out:
            for tag in chunk:
                f_out.write(tag + '\n')
    print(f"成功将 {len(tags)} 个tag拆分到 {file_count} 个文件中，并保存到 '{output_dir}' 目录。")

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    input_file = filedialog.askopenfilename(
        title='选择要拆分的tag文件',
        filetypes=[('文本文件', '*.txt'), ('所有文件', '*.*')]
    )

    if input_file:
        split_tags_to_files(input_file)
    else:
        print("未选择文件，程序退出。")


