from elsapy.elsclient import ElsClient
from elsapy.elsdoc import AbsDoc
import json

# 1. 读取配置
with open("config.json") as con_file:
    config = json.load(con_file)

# 2. 初始化 client
client = ElsClient(config['apikey'])
client.inst_token = config.get('insttoken', '')

# 3. 用 DOI 初始化 AbsDoc
doi = "10.1016/S1525-1578(10)60571-5"  # 这里换成你自己的 DOI
abs_doc = AbsDoc(doi=doi)

# 4. 读取文献数据
if abs_doc.read(client):
    print("Title:", abs_doc.title)
    print("Abstract:", abs_doc.data.get('coredata', {}).get('dc:description', 'No abstract found'))
else:
    print("Read document failed.")