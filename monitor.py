import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

URL = "https://www.51kanong.com/yh-169-1.htm"

WXPUSHER_TOKEN = os.environ.get("WXPUSHER_TOKEN")
WXPUSHER_UID = os.environ.get("WXPUSHER_UID")

def fetch_deals():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.51kanong.com/",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    # 创建带自动重试机制的 Session，应对网络波动
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))

    try:
        # 将超时时间延长到 20 秒
        res = session.get(URL, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        
        if "reload()" in res.text:
            print("检测到防爬 JS 挑战，正在模拟浏览器二次请求...")
            time.sleep(1.5)
            res = session.get(URL, headers=headers, timeout=20)
            res.encoding = 'utf-8'

        soup = BeautifulSoup(res.text, 'html.parser')
        deals = []
        
        for a in soup.find_all('a'):
            title = a.get_text(strip=True)
            href = a.get('href')
            # 过滤掉短标题和非线报链接
            if title and len(title) > 6 and href and not any(w in title for w in ["首页", "登录", "注册", "关于", "导航"]):
                if not href.startswith('http'):
                    href = "https://www.51kanong.com" + (href if href.startswith('/') else '/' + href)
                item = f"• {title}\n  {href}"
                if item not in deals:
                    deals.append(item)
                    
        print(f"成功突破！抓到有效线报条数: {len(deals)}")
        return deals[:10]
    except Exception as e:
        print(f"抓取异常: {e}")
        return []

def send_wxpusher(deals):
    if not WXPUSHER_TOKEN or not WXPUSHER_UID:
        print("未配置 WxPusher 环境变量！")
        return
        
    if not deals:
        print("没有可推送的内容。")
        return

    content = "🐑 51卡农最新羊毛监控：\n\n" + "\n\n".join(deals)
    
    url = "https://wxpusher.zjiecode.com/api/send/message"
    payload = {
        "appToken": WXPUSHER_TOKEN,
        "content": content,
        "summary": "51卡农羊毛实时提醒",
        "contentType": 1,
        "uids": [WXPUSHER_UID]
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        print("微信/App 推送结果返回:", res.text)
    except Exception as e:
        print(f"推送请求失败: {e}")

if __name__ == "__main__":
    print("开始执行 51卡农 监控抓取...")
    deals = fetch_deals()
    if deals:
        print("正在发送推送至手机 App...")
        send_wxpusher(deals)
    else:
        print("未抓取到有效线报。")
