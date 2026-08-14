import pandas as pd
import os
from snownlp import SnowNLP
from gensim import corpora, models
import jieba
import numpy as np
from matplotlib import pyplot as plt
import itertools

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def cos(vector1, vector2):
    dot_product = 0.0
    normA = 0.0
    normB = 0.0
    for a, b in zip(vector1, vector2):
        dot_product += a * b
        normA += a ** 2
        normB += b ** 2
    if normA == 0.0 or normB == 0.0:
        return None
    else:
        return dot_product / ((normA * normB) ** 0.5)
    
def load_keywords_with_sentiment():
    """加载关键词并进行情感分析"""
    data = []
    file_path = 'products\\all_products_keywords.txt'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                keyword, frequency = line.split(':')
                # 使用SnowNLP进行情感分析
                sentiment_score = SnowNLP(keyword).sentiments
                if sentiment_score >= 0.6:
                    sentiment = 'pos'
                elif sentiment_score <= 0.4:
                    sentiment = 'neg'
                else:
                    sentiment = 'neu'
                    
                data.append({
                    'keyword': keyword,
                    'frequency': int(frequency),
                    'sentiment': sentiment
                })
    
    return pd.DataFrame(data)

def create_corpus_by_sentiment(df, sentiment):
    """为特定情感创建语料库"""
    sentiment_data = df[df['sentiment'] == sentiment]
    dictionary = corpora.Dictionary([[word] for word in sentiment_data['keyword']])
    
    # 根据词频创建语料库
    corpus = [dictionary.doc2bow([word]) for word in sentiment_data['keyword'] 
             for _ in range(sentiment_data[sentiment_data['keyword'] == word]['frequency'].values[0])]
    
    return corpus, dictionary

def LDA_k(x_corpus, x_dict):
    """LDA主题数寻优函数"""
    mean_similarity = [1]
    
    for i in range(2, 11):
        lda = models.LdaModel(x_corpus, num_topics=i, id2word=x_dict)
        
        top_word = []
        for k in range(i):
            top_word.append([word[0] for word in lda.show_topic(k, 50)])
        
        word = sum(top_word, [])
        unique_word = set(word)
        
        mat = []
        for j in range(i):
            top_w = top_word[j]
            mat.append(tuple([top_w.count(k) for k in unique_word]))
        
        p = list(itertools.permutations(range(i), 2))
        y = len(p)
        top_similarity = [0]
        for w in range(y):
            vector1 = mat[p[w][0]]
            vector2 = mat[p[w][1]]
            cos_sim = cos(vector1, vector2)
            if cos_sim is not None:
                top_similarity.append(cos_sim)
        
        if len(top_similarity) > 1:
            mean_similarity.append(sum(top_similarity) / (y))
    
    return mean_similarity

def analyze_sentiment_distribution(df):
    """分析情感分布并生成图表"""
    # 计算情感分布
    sentiment_counts = df['sentiment'].value_counts()
    total = len(df)
    sentiment_dist = {
        'pos': sentiment_counts.get('pos', 0) / total,
        'neu': sentiment_counts.get('neu', 0) / total,
        'neg': sentiment_counts.get('neg', 0) / total
    }
    
    # 保存到Excel
    dist_df = pd.DataFrame({
        '情感类型': ['正面', '中性', '负面'],
        '数量': [sentiment_counts.get('pos', 0), sentiment_counts.get('neu', 0), sentiment_counts.get('neg', 0)],
        '占比': [sentiment_dist['pos'], sentiment_dist['neu'], sentiment_dist['neg']]
    })
    dist_df.to_excel('sentiment_distribution.xlsx', index=False)
    
    # 绘制情感分布饼图
    plt.figure(figsize=(10, 6))
    plt.pie([sentiment_dist['pos'], sentiment_dist['neu'], sentiment_dist['neg']],
            labels=['正面', '中性', '负面'],
            autopct='%1.1f%%',
            colors=['#2ecc71', '#f1c40f', '#e74c3c'])
    plt.title('关键词情感分布')
    plt.savefig('sentiment_distribution_pie.png')
    plt.close()
    
    # 绘制情感分数分布直方图
    plt.figure(figsize=(10, 6))
    sentiment_scores = [SnowNLP(keyword).sentiments for keyword in df['keyword']]
    plt.hist(sentiment_scores, bins=20, color='#fece0c', edgecolor='black')
    plt.title('情感分数分布')
    plt.xlabel('情感分数')
    plt.ylabel('频次')
    plt.savefig('sentiment_scores_hist.png')
    plt.close()

def main():
    # 加载数据并进行情感分析
    review_mltype = load_keywords_with_sentiment()
    
    # 分析情感分布
    analyze_sentiment_distribution(review_mltype)
    
    # 为每种情感创建语料库
    sentiments = ['pos', 'neu', 'neg']
    best_topics = {}
    
    for sentiment in sentiments:
        corpus, dictionary = create_corpus_by_sentiment(review_mltype, sentiment)
        
        if len(corpus) < 10:  # 如果样本太少，跳过
            print(f"{sentiment}情感的样本数量不足，跳过分析")
            continue
            
        # 计算最佳主题数
        k_values = LDA_k(corpus, dictionary)
        best_k = k_values.index(min(k_values[1:])) + 1
        best_topics[sentiment] = best_k
        
        # 训练LDA模型
        lda = models.LdaModel(corpus, num_topics=best_k, id2word=dictionary)
        
        # 保存结果
        with open(f'lda_results_{sentiment}.txt', 'w', encoding='utf-8') as f:
            f.write(f"{sentiment}情感的主题分析结果（最佳主题数：{best_k}）：\n\n")
            for topic_id in range(best_k):
                topic = lda.show_topic(topic_id, 10)
                f.write(f"主题 {topic_id + 1}:\n")
                for word, prob in topic:
                    f.write(f"{word}: {prob:.4f}\n")
                f.write("\n")
        
        print(f"{sentiment}情感的LDA分析完成，结果已保存到lda_results_{sentiment}.txt")

if __name__ == "__main__":
    main()