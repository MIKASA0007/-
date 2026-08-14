import os
import jieba
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
from textrank4zh import TextRank4Keyword
import re


# 读取停用词表
def load_stopwords(file_paths):
    """
    从多个文件中读取停用词表。

    参数:
    file_paths (list): 停用词文件的路径列表。

    返回:
    set: 停用词集合。
    """
    stopwords = set()
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            stopwords.update(line.strip() for line in file)
    return stopwords


# 分词函数
def preprocess_text(text, stopwords):
    """
    对文本进行分词处理，并过滤停用词。

    参数:
    text (str): 待分词的文本。
    stopwords (set): 停用词集合。

    返回:
    str: 分词后的文本，词与词之间用空格分隔。
    """
    words = jieba.lcut(text)
    filtered_words = [word for word in words if word not in stopwords]
    return ' '.join(filtered_words)


# 提取TF-IDF关键词
def extract_keywords_tfidf(data, stopwords):
    """
    使用TF-IDF方法提取关键词。

    参数:
    data (pandas.DataFrame): 包含评论数据的DataFrame。
    stopwords (set): 停用词集合。

    返回:
    list: 提取的关键词列表，每个元素为一个元组，包含关键词及其TF-IDF值。
    """
    data['评论'] = data['评论'].apply(lambda x: preprocess_text(x, stopwords))
    vectorizer = TfidfVectorizer(max_features=500)
    tfidf_matrix = vectorizer.fit_transform(data['评论'])
    feature_names = vectorizer.get_feature_names_out()

    tfidf_scores = tfidf_matrix.sum(axis=0)
    keywords = [(feature_names[i], tfidf_scores[0, i]) for i in range(len(feature_names))]
    keywords.sort(key=lambda x: x[1], reverse=True)
    return keywords


# 提取TextRank关键词
def extract_keywords_textrank(data, stopwords):
    """
    使用TextRank方法提取关键词。

    参数:
    data (pandas.DataFrame): 包含评论数据的DataFrame。
    stopwords (set): 停用词集合。

    返回:
    list: 提取的关键词列表，每个元素为一个元组，包含关键词及其出现频率。
    """
    def extract_keywords_textrank_single(text):
        tr4w = TextRank4Keyword()
        tr4w.analyze(text=text, lower=True)
        return tr4w.get_keywords(500, word_min_len=1)

    all_keywords = [extract_keywords_textrank_single(comment) for comment in data['评论']]
    all_keywords = [item for sublist in all_keywords for item in sublist]

    keyword_counts = Counter([keyword.word for keyword in all_keywords if keyword.word not in stopwords])
    return keyword_counts.most_common(500)


def clean_comment(text):
    """
    清洗评论文本。
    
    参数:
    text (str): 原始评论文本
    
    返回:
    str: 清洗后的文本，如果是无效评论则返回空字符串
    """
    if not isinstance(text, str):
        return ''
        
    # 去除URL
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # 去除特殊字符和多余空白
    text = re.sub(r'[\s]+', ' ', text)
    text = text.strip()
    
    # 定义无效评论的模式
    invalid_patterns = [
        r'[.。]{3,}',  # 省略号
        r'^[a-zA-Z0-9]+$',  # 纯数字或字母
        r'(淘宝|天猫|拼多多|京东|优惠券|优惠活动|抢购|秒杀)',  # 广告关键词
        r'[0-9a-zA-Z]+'  # 包含数字和字母的组合
    ]
    
    # 检查是否为无效评论
    for pattern in invalid_patterns:
        if re.search(pattern, text):
            return ''
            
    # 检查评论长度
    if len(text) < 2:  # 过短的评论
        return ''
        
    return text


def process_data(data):
    """
    处理数据框，清洗评论并删除重复内容。
    
    参数:
    data (pandas.DataFrame): 原始数据框
    
    返回:
    pandas.DataFrame: 清洗后的数据框
    """
    # 清洗评论
    data['评论'] = data['评论'].apply(clean_comment)
    
    # 删除空评论
    data = data[data['评论'].str.len() > 0]
    
    # 删除重复评论
    data = data.drop_duplicates(subset=['评论'])
    
    return data


# 主函数
def main():
    urls_id = [
        '100037239863', '100155025054', '10088610057010', '100116666531'
    ]
    file_paths = ['stop_words\\scu_stopwords.txt', 'stop_words\\cn_stopwords.txt']
    stopwords = load_stopwords(file_paths)

    total_original_comments = 0
    total_cleaned_comments = 0

    for url_id in urls_id:
        # 读取数据
        data = pd.read_excel(f"products\\{url_id}\\{url_id}_comment_data.xlsx", 
                           names=["产品名称", "时间", "地点", '评论', '分数'])
        
        # 清洗数据
        cleaned_data = process_data(data)
        
        # 累计评论数
        total_original_comments += len(data)
        total_cleaned_comments += len(cleaned_data)
        
        # 保存清洗后的数据
        cleaned_data.to_excel(f"products\\{url_id}\\{url_id}_cleaned_comment_data.xlsx", index=False)
        
        print(f"处理{url_id}的数据：")
        print(f"原始评论数：{len(data)}")
        print(f"清洗后评论数：{len(cleaned_data)}\n")

        # 提取TF-IDF关键词
        tfidf_keywords = extract_keywords_tfidf(cleaned_data, stopwords)

        # 提取TextRank关键词
        textrank_keywords = extract_keywords_textrank(cleaned_data, stopwords)

        # 保存TF-IDF关键词到文件
        with open(f"products\\{url_id}\\{url_id}_tfidf_keywords.txt", 'w', encoding='utf-8') as f:
            for keyword, score in tfidf_keywords[:100]:
                f.write(f"{keyword}: {score}\n")

        # 保存TextRank关键词到文件
        with open(f"products\\{url_id}\\{url_id}_textrank_keywords.txt", 'w', encoding='utf-8') as f:
            for keyword, count in textrank_keywords[:100]:
                f.write(f"{keyword}: {count}\n")

    # 输出总评论数统计
    print("\n总体统计：")
    print(f"原始总评论数：{total_original_comments}")
    print(f"清洗后总评论数：{total_cleaned_comments}")
    print(f"清洗后保留比例：{(total_cleaned_comments/total_original_comments*100):.2f}%")


if __name__ == "__main__":
    main()
