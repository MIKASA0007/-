import jieba
from wordcloud import WordCloud
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import os
from collections import Counter

# 读取 rank 频率文档并提取关键词及其频率
def extract_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    keywords = {}
    for line in lines:
        keyword, freq = line.strip().split(':')
        keywords[keyword] = int(freq)
    return keywords


# 生成词云图
max_word = 150
background_image = np.array(Image.open('001.png'))  # 确保图片文件存在

def generate_wordcloud(top_keywords, output_path):
    # 计算高频阈值（取频率前20%作为高频词）
    sorted_freq = sorted(top_keywords.values(), reverse=True)
    threshold_index = int(len(sorted_freq) * 0.05)
    threshold = sorted_freq[threshold_index] if threshold_index < len(sorted_freq) else 0

    # 自定义颜色函数
    def color_func(word, **kwargs):
        return '#ce4d4d' if top_keywords.get(word, 0) >= threshold else '#e39a94'

    # 生成词云对象
    wordcloud = WordCloud(
        font_path='simhei.ttf',
        background_color='white',
        max_words=max_word,
        max_font_size=100,
        width=800,
        height=400,
        collocations=False,
        mask=background_image,
        color_func=color_func  # 应用自定义颜色映射
    ).generate_from_frequencies(top_keywords)

    # 显示词云图
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

    # 保存词云图
    wordcloud.to_file(output_path)

# 主函数
def main():
    rank_file_path = 'rank_frequency.txt'
    output_path = 'wordcloud.png'

    keywords = extract_keywords(rank_file_path)
    generate_wordcloud(keywords, output_path)
    print(f"词云图已生成并保存到 {output_path}")
    print(f"总关键词数量: {len(keywords)}")

if __name__ == "__main__":
    main()