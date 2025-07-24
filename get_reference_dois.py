import requests
import json  
import csv
from tqdm import tqdm

input_csv = '/share/zj/ele_extract_zj/Li_metal_selection/abstract.csv'
output_csv = '/share/zj/ele_extract_zj/Li_metal_selection/reference_dois.csv'
ref_doi_txt = '/share/zj/ele_extract_zj/Li_metal_selection/ref_doi.txt'

last_ref_doi = None
try:
    with open(ref_doi_txt, 'r', encoding='utf-8') as f:
        last_ref_doi = f.read().strip()
except FileNotFoundError:
    pass

# 手动输入起始 DOI（可选）
manual_doi = input("请输入要从哪个DOI开始（留空则自动断点续传）: ").strip()
if manual_doi:
    last_ref_doi = manual_doi

doi_list = []
with open(input_csv, 'r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        doi = row.get('DOI')
        if doi:
            doi_list.append(doi.strip())


start_index = 0
if last_ref_doi and last_ref_doi in doi_list:
    start_index = doi_list.index(last_ref_doi) + 1

all_reference_dois = set()

with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    csvfile.seek(0, 2)
    if csvfile.tell() == 0:
        writer.writerow(['DOI'])
    last_written_ref_doi = None
    # 设置 tqdm 的 total 和 initial
    for doi in tqdm(doi_list[start_index:], desc="Processing DOIs", total=len(doi_list), initial=start_index):
        try:
            response = requests.get(
                f"https://api.crossref.org/works/{doi}",
                headers={
                    "User-Agent": "PaperExtractor/1.0",
                    "Accept": "application/json"
                }
            )
            if response.status_code != 200:
                print(f"DOI {doi} 返回状态码: {response.status_code}，跳过。")
                continue
            try:
                data = response.json()
            except Exception as json_err:
                print(f"DOI {doi} JSON解析失败: {json_err}，跳过。")
                continue
            reference_dois = data['message'].get('reference', [])
            for ref in reference_dois:
                ref_doi = ref.get('DOI')
                if ref_doi and ref_doi not in all_reference_dois:
                    all_reference_dois.add(ref_doi)
                    writer.writerow([ref_doi])
                    last_written_ref_doi = doi
                    # 每次写入都更新 ref_doi.txt
                    with open(ref_doi_txt, 'w', encoding='utf-8') as f:
                        f.write(doi)
        except Exception as e:
            print(f"处理DOI {doi} 时出错: {e}")


