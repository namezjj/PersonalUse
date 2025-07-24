import json
import os
import csv
from google import genai
from google.oauth2 import service_account
from tqdm import tqdm

class GeminiClient:
    def __init__(self):
        os.environ["http_proxy"] = "http://ga.dp.tech:8118"
        os.environ["https_proxy"] = "http://ga.dp.tech:8118"
        credentials = service_account.Credentials.from_service_account_file(
            'ele_gemini.json',
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        self.client = genai.Client(
            credentials=credentials,
            project="battery-20250509",
            location='us-central1',
            vertexai=True
        )

    def classify_li_metal(self, abstract):
        if not abstract:
            return False
        prompt = (
            "You are an expert in battery science. "
            "Read the following academic paper abstract and answer only true or false: "
            "Is this paper about lithium metal batteries or closely related technologies? "
            "Abstract: " + abstract
        )
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=[prompt],
            )
            result = response.text.strip().lower()
            return result.startswith("true")
        except:
            return False

def process_papers():
    json_file = '/share/zj/ele_extract_zj/Li_metal_selection/all.json'
    output_csv = '/share/zj/ele_extract_zj/Li_metal_selection/classification_results.csv'
    gemini = GeminiClient()
    with open(json_file, 'r') as f:
        data = json.load(f)
    results = []
    for item in tqdm(data, desc="Processing papers", unit="paper"):
        doi = item.get('DOI', 'Unknown')
        abstract = item.get('Abstract', '')
        is_li_metal = gemini.classify_li_metal(abstract)
        results.append({
            'DOI': doi,
            'is_Li_metal': is_li_metal
        })
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['DOI', 'is_Li_metal']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

if __name__ == "__main__":
    process_papers()