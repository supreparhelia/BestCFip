import requests
from bs4 import BeautifulSoup
import re, os, ipaddress, random, uuid
from datetime import datetime, timedelta
myID = uuid

# ✅ URL源与简称
sources = {
    'https://api.uouin.com/cloudflare.html': 'Uouin',
    'https://ip.164746.xyz': 'ZXW',
    'https://raw.githubusercontent.com/ymyuuu/IPDB/main/BestCF/bestcfv4.txt': 'IPDB',
    'https://www.wetest.vip/page/cloudflare/address_v6.html': 'WetestV6',
    'https://hhhhh.eu.org/030101-bestcf.txt': 'bCF',
    'https://hhhhh.eu.org/CloudFlareYes.txt': 'CFYes',
    'https://hhhhh.eu.org/haogege.txt': 'HaoGG',
    'https://hhhhh.eu.org/vps789.txt': 'VPS',
    'https://hhhhh.eu.org/wetest-cloudflare-v4.txt': 'WeTest'
}

PORT = '443'  # 目标端口号

# 正则表达式
ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
ipv6_candidate_pattern = r'([a-fA-F0-9:]{2,39})'

headers = {
    'User-Agent': 'Mozilla/5.0'
}

# 删除旧文件
for file in ['ipv4.txt', 'ipv6.txt']:
    if os.path.exists(file):
        os.remove(file)

# IP 分类存储
ipv4_dict = {}
ipv6_dict = {}

# 当前时间
utctimestamp = datetime.now().strftime('%Y%m%d%H%M')
beijing_time = datetime.utcnow() + timedelta(hours=8)
now_str = beijing_time.strftime('%Y-%m-%d_%H:%M')
timestamp = beijing_time.strftime('%Y%m%d_%H:%M')

# 遍历来源
for url, shortname in sources.items():
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        content = response.text

        if url.endswith('.txt'):
            text = content
        else:
            soup = BeautifulSoup(content, 'html.parser')
            elements = soup.find_all('tr') or soup.find_all('li')
            text = '\n'.join(el.get_text() for el in elements)

        # IPv4 提取
        for ip in re.findall(ipv4_pattern, text):
            try:
                if ipaddress.ip_address(ip).version == 4:
                    ip_with_port = f"{ip}:{PORT}"
                    comment = f"{shortname}-{myID.uuid4().hex[27:]}{str(random.randint(0,10))}"
                    ipv4_dict[ip_with_port] = comment
            except ValueError:
                continue

        # IPv6 提取
        for ip in re.findall(ipv6_candidate_pattern, text):
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.version == 6:
                    ip_with_port = f"[{ip_obj.compressed}]:{PORT}"
                    comment = f"IPv6-{shortname}-{myID.uuid4().hex[27:]}{str(random.randint(0,10))}"
                    ipv6_dict[ip_with_port] = comment
            except ValueError:
                continue

    except requests.RequestException as e:
        print(f"[请求错误] {url} -> {e}")
    except Exception as e:
        print(f"[解析错误] {url} -> {e}")

# 写入 ipv4.txt（仅IPv4）
with open('ipv4.txt', 'w') as f4:
    f4.write(f"0.0.0.0:000#Updated{now_str}\n")
    for ip in sorted(ipv4_dict):
        f4.write(f"{ip}#{ipv4_dict[ip]}\n")

# 写入 ipv6.txt（仅IPv6）
with open('ipv6.txt', 'w') as f6:
    f6.write(f"0.0.0.0:000#Updated{now_str}\n")
    for ip in sorted(ipv6_dict):
        f6.write(f"{ip}#{ipv6_dict[ip]}\n")

print(f"✅ IPv4 写入 ipv4.txt，共 {len(ipv4_dict)} 个")
print(f"✅ IPv6 写入 ipv6.txt，共 {len(ipv6_dict)} 个")
