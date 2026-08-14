# 电商评论采集、文本挖掘与情感主题分析

本项目以京东商品评论为数据源，完成从评论采集、清洗和关键词提取，到词云、情感分布和 LDA 主题分析的一条完整流程。

## 完整流程文件

根目录中以下 4 个编号脚本构成主流程，应按序运行：

| 步骤 | 文件 | 功能 | 主要输入 | 主要输出 |
| --- | --- | --- | --- | --- |
| 1 | `1_comment_grabbing.py` | 请求京东评论接口，按商品采集评论 | 脚本中的 `urls_id` | `products/<商品ID>/<商品ID>_comment_data.xlsx` |
| 2 | `2_Key word.py` | 清洗、去重、分词，并用 TF-IDF 和 TextRank 提取关键词 | 原始评论 Excel、`stop_words/` | 清洗后的评论 Excel、两类关键词 TXT |
| 3 | `3_cloud word.py` | 汇总各商品 TextRank 关键词并生成词云 | 各商品的 `*_textrank_keywords.txt`、停用词、`001.png` | `products/all_products_keywords.txt`、`products/all_products_wordcloud.png` |
| 4 | `4_sentiment_topic_analysis.py` | 对汇总关键词进行 SnowNLP 情感分类并按情感做 LDA 主题分析 | `products/all_products_keywords.txt` | 情感分布 Excel/图片、正/中/负主题结果 TXT |


## 目录说明

```text
.
├─ 1_comment_grabbing.py              # 评论采集
├─ 2_Key word.py                      # 清洗与关键词提取
├─ 3_cloud word.py                    # 汇总关键词并绘制词云
├─ 4_sentiment_topic_analysis.py      # 情感分析与 LDA 主题建模
├─ products/                          # 每个商品的中间数据与汇总结果
├─ stop_words/                        # 中文停用词表
├─ 001.png                            # 词云遮罩图
└─ 产出分析/                           # 已生成的分析结果示例
```

## 环境准备

建议使用 Python 3.9+，在项目根目录安装依赖：

```bash
pip install requests pandas openpyxl jieba scikit-learn textrank4zh wordcloud pillow matplotlib snownlp gensim numpy scipy
```

词云和图表使用中文字体。Windows 通常可将脚本中的 `font_path='simhei.ttf'` 改为系统字体完整路径，例如 `C:/Windows/Fonts/simhei.ttf`；同时请确保 `001.png` 位于项目根目录。

## 运行方法

在项目根目录依次运行：

```bash
python "1_comment_grabbing.py"
python "2_Key word.py"
python "3_cloud word.py"
python "4_sentiment_topic_analysis.py"
```

### 运行前配置

1. 在 `1_comment_grabbing.py` 的 `urls_id` 中填写要采集的京东商品 ID；商品 ID 同时必须出现在后续两个脚本的列表中。
2. `2_Key word.py` 当前使用 4 个商品 ID：`100037239863`、`100155025054`、`10088610057010`、`100116666531`。
3. `3_cloud word.py` 中的 `product_ids` 目前含有 11 个 ID，但项目现有数据只有上述 4 个。首次运行前，请将该列表改为与步骤 1、2 完全一致的 4 个 ID；不存在的 ID 会被自动跳过，但保持一致可避免结果不完整。
4. `4_sentiment_topic_analysis.py` 默认将结果写入当前工作目录。若希望与现有示例一致，请将输出文件路径统一改到 `产出分析/`，或在该目录中执行此脚本并相应调整输入路径。

## 数据流

```text
京东评论接口
  → 原始评论 Excel
  → 清洗后的评论 Excel + TF-IDF/TextRank 关键词
  → 汇总关键词文本 + 词云图
  → 情感分布图表 + 正/中/负 LDA 主题结果
```

## 结果说明

- `*_cleaned_comment_data.xlsx`：清洗、去重后的评论数据。
- `*_tfidf_keywords.txt`：单个商品的 TF-IDF 关键词及权重。
- `*_textrank_keywords.txt`：单个商品的 TextRank 关键词及出现频次。
- `all_products_keywords.txt`：所有商品关键词频次汇总，是后续分析的唯一输入。
- `all_products_wordcloud.png`：汇总关键词的词云图。
- `sentiment_distribution.xlsx`、`sentiment_distribution_pie.png`、`sentiment_scores_hist.png`：关键词的情感分类统计与可视化。
- `lda_results_pos.txt`、`lda_results_neu.txt`、`lda_results_neg.txt`：三个情感类别下的主题词及其概率。

## 注意事项

- 评论采集依赖第三方网站接口，接口返回格式、访问频率限制或反爬策略变化可能导致采集失败。请控制访问频率并遵守网站规则。
- 现有流程对“汇总关键词”而不是完整评论句子进行情感和 LDA 分析，结论适合用于探索性洞察；若用于严谨研究，建议以清洗后的完整评论为分析单位。
- 重新运行步骤 1 会写入已有 Excel；如需避免重复数据，建议先备份或清空对应商品目录中的旧原始评论文件。
