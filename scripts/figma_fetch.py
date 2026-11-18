# -*- coding: utf-8 -*-
"""Figma 原型拉取器 —— test-case-designer skill 配套脚本。

用法:
    python figma_fetch.py <figma_url> --pages                 # 列出页面
    python figma_fetch.py <figma_url> --frames <page_id>      # 列出页面下顶层Frame
    python figma_fetch.py <figma_url> --texts <fid,fid,...>   # 提取Frame文本(去重)
    python figma_fetch.py <figma_url> --tree <fid>            # Frame层级+文本

token 自动读取顺序:~/.zcode/cli/config.json 的 mcp.servers.figma-dev.env.FIGMA_API_KEY
→ 环境变量 FIGMA_API_KEY → 提示用户提供。URL 中 node-id 的 `-` 自动转 `:`。
"""
import argparse
import json
import os
import sys
import urllib.request

# Windows GBK 终端兼容:原型文本常含 emoji,防 UnicodeEncodeError
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://api.figma.com/v1"
CONFIG = os.path.expanduser("~/.zcode/cli/config.json")


def get_token():
    if os.environ.get("FIGMA_API_KEY"):
        return os.environ["FIGMA_API_KEY"]
    try:
        cfg = json.load(open(CONFIG, encoding="utf-8"))
        tok = cfg["mcp"]["servers"]["figma-dev"]["env"]["FIGMA_API_KEY"]
        if tok:
            return tok
    except (OSError, KeyError, json.JSONDecodeError):
        pass
    print("未找到 FIGMA_API_KEY(配置与环境变量均无)。", file=sys.stderr)
    print("请提供 Figma personal access token:", file=sys.stderr)
    return input().strip()


def api(token, path):
    req = urllib.request.Request(BASE + path, headers={"X-Figma-Token": token})
    return json.load(urllib.request.urlopen(req, timeout=60))


def parse_key(url):
    # https://www.figma.com/design/<key>/Name?node-id=0-1
    for part in url.split("/"):
        if len(part) > 10 and "-" not in part and part.isalnum():
            return part
    raise SystemExit("无法从 URL 提取 file key: %s" % url)


def norm_ids(raw):
    return [i.strip().replace("-", ":") for i in raw.split(",") if i.strip()]


def collect_texts(node, out, seen):
    if node.get("type") == "TEXT":
        t = (node.get("characters") or "").strip()
        if t and t not in seen:
            seen.add(t)
            out.append({"frame": node.get("name", ""), "text": t})
    for ch in node.get("children", []):
        collect_texts(ch, out, seen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--pages", action="store_true")
    ap.add_argument("--frames")
    ap.add_argument("--texts")
    ap.add_argument("--tree")
    args = ap.parse_args()

    token = get_token()
    key = parse_key(args.url)

    if args.pages:
        d = api(token, "/files/%s?depth=2" % key)
        for p in d["document"]["children"]:
            print("%s\t%s\tchildren=%d" % (p["id"], p["name"], len(p.get("children", []))))
    elif args.frames:
        pid = args.frames.replace("-", ":")
        d = api(token, "/files/%s/nodes?ids=%s&depth=2" % (key, pid))
        for ch in d["nodes"][pid]["document"].get("children", []):
            print("%s\t%s\t%s" % (ch["id"], ch["name"], ch["type"]))
    elif args.texts:
        ids = norm_ids(args.texts)
        d = api(token, "/files/%s/nodes?ids=%s" % (key, ",".join(ids)))
        for nid in ids:
            doc = d["nodes"][nid]["document"]
            out, seen = [], set()
            collect_texts(doc, out, seen)
            print("==== %s (%s) ====" % (doc.get("name", nid), nid))
            for item in out:
                print("  [%s] %s" % (item["frame"][:24], item["text"][:80]))
    elif args.tree:
        nid = args.tree.replace("-", ":")
        d = api(token, "/files/%s/nodes?ids=%s" % (key, nid))
        doc = d["nodes"][nid]["document"]

        def walk(n, depth=0):
            t = (n.get("characters") or "").strip() if n.get("type") == "TEXT" else ""
            label = ("%sTEXT: %s" % (" " * (depth + 1) * 2, t[:60]) if t
                     else "%s%s (%s)" % (" " * depth * 2, n.get("name", "?")[:40], n.get("type", "")))
            print(label)
            for ch in n.get("children", []):
                walk(ch, depth + 1)
        walk(doc)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
