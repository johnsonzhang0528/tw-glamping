#!/usr/bin/env python3
"""
seo_risk_scan.py  (T5.5 — SEO 風險自我監理掃描器)

用途:
    定期檢查資料層是否出現「會被 Google 判定為 spam-pattern」的風險,
    讓站台自我監理、及早發現問題。純讀取,不修改任何資料。

檢查項目:
    1. 重複描述比例(description 完全相同/高度重複)
    2. 薄頁(description 過短 / tags 過少 / 缺座標)
    3. 缺關鍵欄位(city / elevation / lat / lng)
    4. 模板同構風險(描述開頭 n-gram 過度集中)

狀態:
    獨立腳本,**未**接入 CI。可手動執行,或日後自行接入週更管線。

用法:
    python py/seo_risk_scan.py            # 印報告到 stdout
    python py/seo_risk_scan.py --md       # 額外輸出 markdown 報告到 .sop/tw-glamping/
"""
import json
import os
import sys
import collections
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMPS_PATH = os.path.join(BASE_DIR, "..", "src", "data", "campgrounds_smart_clean.json")
# 報告輸出位置(相對於整個 workspace 的 .sop)
REPORT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", ".sop", "tw-glamping"))

THIN_DESC_LEN = 40
MIN_TAGS = 2


def scan(camps):
    n = len(camps)
    issues = collections.OrderedDict()

    # 1. 重複描述
    desc_counter = collections.Counter(c.get("description", "").strip() for c in camps)
    dup_descs = {d: cnt for d, cnt in desc_counter.items() if d and cnt > 1}
    dup_pages = sum(cnt for cnt in dup_descs.values())
    issues["重複描述"] = {
        "count": dup_pages,
        "detail": f"{len(dup_descs)} 組完全相同描述,涉及 {dup_pages} 頁",
        "ratio": round(dup_pages / n * 100, 1) if n else 0,
    }

    # 2. 薄頁
    thin = [c["name"] for c in camps
            if len(c.get("description", "").strip()) < THIN_DESC_LEN
            or len(c.get("tags", [])) < MIN_TAGS
            or not (c.get("lat") and c.get("lng"))]
    issues["薄頁(desc<%d/tags<%d/缺座標)" % (THIN_DESC_LEN, MIN_TAGS)] = {
        "count": len(thin),
        "detail": "、".join(thin[:10]) + (" …" if len(thin) > 10 else "") if thin else "無",
        "ratio": round(len(thin) / n * 100, 1) if n else 0,
    }

    # 3. 缺關鍵欄位
    missing = [c.get("name", "?") for c in camps
               if not c.get("city") or not c.get("elevation") or not c.get("lat") or not c.get("lng")]
    issues["缺關鍵欄位(city/elevation/lat/lng)"] = {
        "count": len(missing),
        "detail": "、".join(missing[:10]) + (" …" if len(missing) > 10 else "") if missing else "無",
        "ratio": round(len(missing) / n * 100, 1) if n else 0,
    }

    # 4. 描述開頭同構(前 12 字 n-gram 集中度)
    heads = collections.Counter(c.get("description", "")[:12] for c in camps if c.get("description"))
    top_head, top_cnt = heads.most_common(1)[0] if heads else ("", 0)
    issues["描述開頭同構(前12字最集中者)"] = {
        "count": top_cnt,
        "detail": f'「{top_head}…」出現 {top_cnt} 次' if top_cnt > 1 else "無明顯集中",
        "ratio": round(top_cnt / n * 100, 1) if n else 0,
    }

    return n, issues


def main():
    with open(CAMPS_PATH, encoding="utf-8") as f:
        camps = json.load(f)
    n, issues = scan(camps)

    lines = [f"# tw-glamping SEO 風險掃描報告", "",
             f"掃描時間:{datetime.now().isoformat(timespec='seconds')}",
             f"營區總數:{n}", ""]
    print(f"\n=== SEO 風險掃描({n} 個營區)===")
    for name, r in issues.items():
        flag = "⚠️ " if r["count"] > (n * 0.05) else "✅ "
        line = f"{flag}{name}: {r['count']} 筆({r['ratio']}%) — {r['detail']}"
        print(line)
        lines.append(f"- {flag}**{name}**: {r['count']} 筆({r['ratio']}%) — {r['detail']}")

    if "--md" in sys.argv:
        os.makedirs(REPORT_DIR, exist_ok=True)
        out = os.path.join(REPORT_DIR, f"seo_risk_report_{datetime.now():%Y-%m-%d}.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"\n📄 報告已輸出:{out}")


if __name__ == "__main__":
    main()
