import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.51kanong.com/yh-169-1.htm"

def fetch_deals():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive"
    }
    try:
        res = requests.get(URL, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        print(f"网页请求状态码: {res.status_code}")
        print(f"返回源码前 300 字符: {res.text[:300]}") # 打印出来看看是不是被安全盾拦截了
        
        soup = BeautifulSoup(res.text, 'html.parser')
        deals = []
        
        for a in soup.find_all('a'):
            title = a.get_text(strip=True)
            href = a.get('href')
            if title and href:
                deals.append(f"标题: {title}\n链接: {href}")
                
        print(f"抓取到的链接总数: {len(deals)}")
        return deals[:10]
    except Exception as e:
        print(f"抓取异常: {e}")
        return []

if __name__ == "__main__":
    print("开始最终调试抓取...")
    deals = fetch_deals()
    if deals:
        print("成功获取到内容！")
    else:
        print("依然未获取到内容，请把上方“返回源码前 300 字符”发给我。")
