import pandas as pd

# 读取两个 CSV 文件
df1 = pd.read_csv('/share/zj/ele_extract_zj/Li_metal_selection/ref_dois_final.csv')
df2 = pd.read_csv('/share/zj/ele_extract_zj/Li_metal_selection/abstract.csv')

# 提取 file2 的 DOI 集合
doi_set = set(df2['DOI'].dropna().astype(str))

# 删除 file1 中 DOI 在 file2 中出现的行
df1_filtered = df1[~df1['DOI'].astype(str).isin(doi_set)]

# 保存结果
df1_filtered.to_csv('/share/zj/ele_extract_zj/Li_metal_selection/ref_dois_final_dedup.csv', index=False)

print("去重完成，结果已保存为 ref_dois_final_dedup.csv")
