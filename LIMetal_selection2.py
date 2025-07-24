import json
import os
import csv
from tqdm import tqdm
from google import genai
from google.oauth2 import service_account

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
            "You are an expert in battery science. Carefully read the following academic paper abstract "
            "and determine if this paper's main focus is on lithium metal batteries or lithium-containing materials. "
            "Answer only 'true' or 'false' based on these criteria:\n\n"
            "True if the paper primarily focuses on ANY of these:\n"
            "- Lithium metal anode technology or lithium metal batteries\n"
            "- Lithium-containing electrode materials (e.g., LiCoO2, LiFePO4, Li-rich cathodes)\n"
            "- Lithium-containing electrolytes or salts (e.g., LiPF6, LiTFSI)\n"
            "- Battery systems using lithium-based materials as main components\n"
            "- Development or modification of materials specifically for lithium batteries\n"
            "- Studies of lithium-ion transport or lithium-related mechanisms\n\n"
            "False if:\n"
            "- Lithium materials or batteries are only mentioned as comparison or examples\n"
            "- The paper mainly focuses on non-lithium systems\n"
            "- Lithium compounds are only briefly mentioned but not the main research focus\n"
            "- The work is about general battery concepts without specific focus on lithium systems\n\n"
            "Example of True case: 'LiMn2O4 and LiCoO2 based full cells were investigated for their electrochemical performance...'\n"
            "Example of False case: 'Various battery systems including Li-ion, Na-ion, and K-ion batteries were compared...'\n\n"
            "Abstract: " + abstract + "\n\n"
            "Answer (true/false):"
        )
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[prompt],
            )
            response_text = getattr(response, 'text', None)
            if response_text:
                result = response_text.strip().lower()
                return result.startswith("true")
            return False
        except Exception as e:
            print(f"Error processing abstract: {str(e)}")
            return False

def process_abstracts():
    # Initialize the Gemini client
    client = GeminiClient()
    
    # File paths
    json_file = '/share/zj/ele_extract_zj/Li_metal_selection/abstract60001.json'
    output_csv = '/share/zj/ele_extract_zj/Li_metal_selection/true_dois2.csv'
    progress_file = '/share/zj/ele_extract_zj/Li_metal_selection/progress2.txt'
    
    # Read the JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    
    # Get the starting index from user input
    print(f"\nTotal entries in JSON file: {len(entries)}")
    
    # Read last processed DOI if exists
    last_processed_doi = None
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            last_processed_doi = f.read().strip()
        if last_processed_doi:
            print(f"Last processed DOI: {last_processed_doi}")
    
    start_doi = input("Enter the DOI to start ").strip()
    
    # Find starting index
    start_index = 0
    if start_doi:
        # If user provided a DOI, find its index
        for i, entry in enumerate(entries):
            if entry['DOI'] == start_doi:
                start_index = i
                break
        print(f"Starting from index {start_index} (DOI: {start_doi})")
    elif last_processed_doi:
        # If no DOI provided but we have last processed DOI, start from next one
        for i, entry in enumerate(entries):
            if entry['DOI'] == last_processed_doi:
                start_index = i + 1
                break
        print(f"Continuing from index {start_index}")
    
    # Process each entry with Gemini
    for i, entry in enumerate(tqdm(entries[start_index:], initial=start_index, total=len(entries), desc="Processing with Gemini API")):
        is_li_metal = client.classify_li_metal(entry['Abstract'])
        
        # Save progress
        with open(progress_file, 'w', encoding='utf-8') as f:
            f.write(entry['DOI'])
        
        # If true, append to CSV immediately
        if is_li_metal:
            with open(output_csv, 'a', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write header if file is empty
                if os.path.getsize(output_csv) == 0:
                    writer.writerow(['DOI'])
                writer.writerow([entry['DOI']])
    
    print(f"\nProcessing completed!")
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    process_abstracts()