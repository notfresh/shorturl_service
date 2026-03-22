#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Podcast Markdown to CSV Converter
将 pie-podcast-nav-v2.md 转换为 CSV 文件
"""

import re
import csv
import sys
from pathlib import Path


def parse_markdown_to_csv(input_file: str, output_file: str = None) -> None:
    """
    解析 Markdown 文件为 CSV
    
    Args:
        input_file: 输入的 Markdown 文件路径
        output_file: 输出的 CSV 文件路径（默认同名 .csv）
    """
    if output_file is None:
        output_file = Path(input_file).stem + '.csv'
    
    # 从输入路径推导 submodule 前缀（如 Podcast-Subtitle/pie-podcast-nav-v2.md -> Podcast-Subtitle）
    input_path = Path(input_file)
    subtitle_prefix = str(input_path.parent) if str(input_path.parent) != '.' else ''
    
    # 读取 Markdown 文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ 文件不存在: {input_file}")
        sys.exit(1)
    
    # 解析内容
    episodes = []
    lines = content.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 匹配标题行 [标题](链接)
        title_match = re.match(r'\[(.+?)\]\((.+?)\)', line)
        if title_match and i + 1 < len(lines):
            title = title_match.group(1)
            audio_url = title_match.group(2)
            
            # 下一行应该是字幕行
            next_line = lines[i + 1].strip()
            subtitle_match = re.match(r'\[(.+?)\]\((.+?)\)', next_line)
            
            if subtitle_match:
                subtitle_text = subtitle_match.group(1)
                subtitle_url = subtitle_match.group(2)
                
                # 将 ./pie-srt/... 转换为 Podcast-Subtitle/pie-srt/... 相对于项目根目录
                if subtitle_prefix and subtitle_url.startswith('./'):
                    subtitle_url = subtitle_prefix + '/' + subtitle_url[2:]
                
                episodes.append({
                    'title': title,
                    'audio_url': audio_url,
                    'subtitle_text': subtitle_text,
                    'subtitle_url': subtitle_url
                })
                
                i += 2  # 跳过已处理的两行
                continue
        
        i += 1
    
    # 写入 CSV 文件
    if episodes:
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f, 
                    fieldnames=['title', 'audio_url', 'subtitle_text', 'subtitle_url']
                )
                writer.writeheader()
                writer.writerows(episodes)
            
            print(f"✅ 转换完成！")
            print(f"   输入文件: {input_file}")
            print(f"   输出文件: {output_file}")
            print(f"   总条数: {len(episodes)}")
        except IOError as e:
            print(f"❌ 写入文件时出错: {e}")
            sys.exit(1)
    else:
        print(f"❌ 未找到任何有效的条目")
        sys.exit(1)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='将 Podcast Markdown 文件转换为 CSV 格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python podcast_markdown_to_csv.py Podcast-Subtitle/pie-podcast-nav-v2.md
  python podcast_markdown_to_csv.py Podcast-Subtitle/pie-podcast-nav-v2.md -o podcasts.csv
        '''
    )
    
    parser.add_argument(
        'input_file',
        help='输入的 Markdown 文件路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出的 CSV 文件路径（默认为同名 .csv 文件）'
    )
    
    args = parser.parse_args()
    
    parse_markdown_to_csv(args.input_file, args.output)
