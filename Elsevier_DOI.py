import pandas as pd
import re
import csv

df = pd.read_csv('/share/zj/ele_extract_zj/Li_metal_selection/ref_dois_final_dedup.csv')  # 替换为你的 csv 文件名


doi_list = df['DOI'].dropna().astype(str)

pattern = re.compile(r'^10\.1016/j.*')
filtered_dois = [doi for doi in doi_list if pattern.match(doi)]

with open('/share/zj/ele_extract_zj/Li_metal_selection/Elsevier_DOI.csv', 'w', newline='', encoding='utf-8') as f   :
    writer = csv.writer(f)
    writer.writerow(['DOI'])
    for doi in filtered_dois:
        writer.writerow([doi])

print(f"筛选完成，结果已保存到 Elsevier_DOI.csv")
