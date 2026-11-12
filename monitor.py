import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

API_KEY = os.environ.get("AI_API_KEY")
WXPUSHER_TOKEN = os.environ.get("WXPUSHER_TOKEN")
WXPUSHER_UID = os.environ.get("WXPUSHER_UID")

URL = "https://www.51kanong.com/yh-169-1.htm"

def fetch_deals():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.51kanong.com/"
    }
    try:
        res = requests.get(URL, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        print(f"网页请求状态码: {res.status_code}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        deals = []
        
        # 强力兜底：遍历页面中所有的 a 标签，只要包含文字就强行抓取
        for a in soup.find_all('a'):
            title = a.get_text(strip=True)
            href = a.get('href')
            # 放宽条件：只要字数大于 4，且不是纯粹的页码或简单符号
            if title and len(title) > 4 and href:
                if not href.startswith('http'):
                    href = "https://www.51kanong.com" + (href if href.startswith('/') else '/' + href)
                
                item = f"标题: {title}\n链接: {href}"
                if item not in deals:
                    deals.append(item)
                    
        print(f"强力抓取到的链接总数: {len(deals)}")
        return deals[:20] # 获取前 20 条
    except Exception as e:
        print(f"抓取网页异常: {e}")
        return []

def send_wxpusher(content):
    if not WXPUSHER_TOKEN or not WXPUSHER_UID or not content:
        print("未配置推送凭证")
        return
    
    url = "https://wxpusher.zjiecode.com/api/send/message"
    payload = {
        "appToken": WXPUSHER_TOKEN,
        "content": f"🐑 51卡农强力监控通知\n\n{content}",
        "summary": "51卡农线报强力推送",
        "contentType": 1,
        "uids": [WXPUSHER_UID]
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        print("微信推送结果:", res.text)
    except Exception as e:
        print(f"微信推送失败: {e}")

if __name__ == "__main__":
    print("开始强力抓取 51卡农...")
    deals = fetch_deals()
    if deals:
        # 为了确保你能立刻在手机 App 上看到效果，这里直接把抓到的最新内容推送过去
        combined_content = "\n\n----------------\n\n".join(deals[:5])
        print("准备推送抓取到的内容...")
        send_wxpusher(combined_content)
    else:
        print("未抓取到任何有效内容。")
