#!/usr/bin/env python3
"""
indexnow_ping.py  (T4.2 — IndexNow 技術收錄加速)

用途:
    部署後把網站 URL 提交給 IndexNow(Bing / Yandex 等支援;Google 官方未加入
    但提交無害)。純技術收錄加速,Google 官方支持的 sitemap/robots 機制之外的補充。

狀態:
    獨立腳本,**未**接入 CI。可在部署後手動執行,或日後自行接入部署流程。

金鑰:
    public/85bfdc4bcdc388a827ff7bdfb0062b44.txt 已放置於站台根目錄,
    IndexNow 會驗證此檔內容 == key。

用法:
    python py/indexnow_ping.py                 # 提交 sitemap 內所有 URL
    python py/indexnow_ping.py /camp/xxx/ ...   # 只提交指定路徑
"""
import os
import sys
import xml.etree.ElementTree as ET

try:
    import requests
except ImportError:
    print("需要 requests: pip install requests")
    sys.exit(1)

HOST = "www.outdoorcampingworld.com"
KEY = "85bfdc4bcdc388a827ff7bdfb0062b44"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
SITEMAP = f"https://{HOST}/sitemap-0.xml"


def urls_from_sitemap():
    r = requests.get(SITEMAP, timeout=30)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in root.findall(".//sm:loc", ns) if loc.text]


def submit(urls):
    # IndexNow 單次上限 10,000 URL
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls[:10000],
    }
    r = requests.post(ENDPOINT, json=payload, timeout=30)
    print(f"IndexNow 回應:{r.status_code} — 提交 {len(payload['urlList'])} 個 URL")
    if r.status_code not in (200, 202):
        print(r.text[:500])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if args:
        urls = [a if a.startswith("http") else f"https://{HOST}{a}" for a in args]
    else:
        print("從 sitemap 讀取 URL…")
        urls = urls_from_sitemap()
    if not urls:
        print("沒有可提交的 URL。")
        return
    submit(urls)


if __name__ == "__main__":
    main()
