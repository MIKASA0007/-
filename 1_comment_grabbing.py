import requests
import pandas as pd
import os
import time
import random


# 生成一个按 url_id 保存 Excel 文件的路径
def save_comments_to_excel(url_id, comments_data):
    file_path = f'products\\{url_id}\\{url_id}_comment_data.xlsx'

    # 使用 Pandas 将数据保存为 Excel 文件
    df = pd.DataFrame(comments_data)

    # 如果文件已存在，则将数据追加到文件中
    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, mode='a', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=f'Page_{url_id}', index=False)
    else:
        # 如果文件不存在，则直接创建文件并写入数据
        df.to_excel(file_path, index=False)


# 设置请求头来伪装成浏览器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# 循环处理每个商品的评论数据
urls_id = [
        '100037239863', '100155025054', '10088610057010','100116666531'
    ]
for url_id in urls_id:
    # 创建以产品ID命名的文件夹
    product_folder = os.path.join("products", url_id)
    if not os.path.exists(product_folder):
        os.makedirs(product_folder)
    product_info = []
    comments_data = []  # 用于存储当前商品的所有评论数据
    # 将爬取的产品信息添加至excel表格中 不包括评论信息

    for i in range(0, 3):  # 评分
        for j in range(1, 30):  # 页数
            url = f'https://club.jd.com/comment/productPageComments.action?&productId={url_id}&score={i}&sortType=5&page={j}&pageSize=10&isShadowSku=0&fold=1'
            res = requests.get(url, headers=headers)  # 使用 headers 伪装请求
            comments = res.json().get('comments', [])
            for k in comments:
                data = {
                    "产品名称": k["referenceName"],
                    "时间": k['creationTime'],
                    "地点": k.get('location', ''),
                    '评论': k['content'],
                    '分数': k['score'],
                }
                comments_data.append(data)
                print(data)  # 打印当前评论数据

            # 随机延迟（避免请求过快）
            delay = random.uniform(1, 3)  # 随机1-3秒
            print(f'等待 {delay:.2f} 秒...')
            time.sleep(delay)

    # 保存评论数据到对应的 Excel 文件
    save_comments_to_excel(url_id, comments_data)
    print(f'评论数据已保存到 {url_id}_comment_data.xlsx')
