import jieba
from wordcloud import WordCloud
import numpy as np
from PIL import Image
from matplotlib import colors, pyplot as plt
import os
from collections import Counter


# 读取停用词表
def load_stop_words(file_path):
    stop_words = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stop_words.add(line.strip())
    return stop_words


# 读取 rank 频率文档并提取关键词及其频率
def extract_keywords(file_path, stop_words):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    keywords = {}
    for line in lines:
        keyword, freq = line.strip().split(':')
        if keyword not in stop_words:
            keywords[keyword] = int(freq)
    return keywords


# 综合所有产品的关键词
def aggregate_keywords(product_folder, product_ids, stop_words):
    all_keywords = Counter()
    for product_id in product_ids:
        rank_file_path = os.path.join(product_folder, f"{product_id}\\{product_id}_textrank_keywords.txt")
        if os.path.exists(rank_file_path):
            keywords = extract_keywords(rank_file_path, stop_words)
            all_keywords.update(keywords)
    return all_keywords


# 生成词云图
max_word = 500
background_image = np.array(Image.open('001.png'))
def generate_wordcloud(top_keywords, output_path):
    wordcloud = WordCloud(
        font_path='simhei.ttf',  # 字体路径，确保字体文件在可访问的路径中
        background_color='white',  # 背景色
        max_words=max_word,  # 最多显示的词数
        max_font_size=100,  # 最大字号
        width=800,  # 图片宽度
        height=400,  # 图片高度
        collocations=False,  # 是否包括词组
        mask=background_image # 图片形状
    ).generate_from_frequencies(top_keywords)

    # 显示词云图
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # 不显示坐标轴
    plt.show()

    # 保存词云图
    wordcloud.to_file(output_path)


# 主函数
def main():
    products_folder = "products"  # 存放所有产品关键词文件的目录
    product_ids = [
        '100037239863', '100018614939', '100049431059', '100162844432', '100155025054',
        '100071963403', '100029678030', '100128202326', '100011730862', '100101255146',
        '100092264315'
    ]

    # 加载停用词表
    stop_words = load_stop_words('stop_words\\my_stop_words.txt')

    # 综合所有产品的关键词
    all_keywords = aggregate_keywords(products_folder, product_ids, stop_words)
    top_keywords = dict(all_keywords.most_common(max_word))  # 选择频率最高的前 n 个关键词

    # 生成词云图并保存
    output_path = os.path.join(products_folder, "all_products_wordcloud.png")
    generate_wordcloud(top_keywords, output_path)
    print(f"综合所有产品的词云图已生成并保存到 {output_path}")
    print(f"总关键词数量: {len(all_keywords)}")

    # 将关键词保存为txt文件
    keywords_txt_path = os.path.join(products_folder, "all_products_keywords.txt")
    with open(keywords_txt_path, 'w', encoding='utf-8') as f:
        for keyword, freq in all_keywords.items():
            f.write(f"{keyword}:{freq}\n")
    print(f"关键词已保存到 {keywords_txt_path}")


if __name__ == "__main__":
    main()
