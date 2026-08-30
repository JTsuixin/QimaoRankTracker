# -*- coding: utf-8 -*-
"""
七猫免费小说榜单抓取脚本
榜单页面为服务端渲染的静态 HTML，直接 requests + BeautifulSoup 解析即可，
无需无头浏览器，也没有字体反爬。

榜单体系: https://www.qimao.com/paihang/{boy|girl}/{new|hot|over|collect}/date/
输出: data/qimao_ranks_YYYYMMDD.json
"""
import os
import json
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 榜单定义: (频道标签, 榜单路由, 展示名, channel 字段)
RANKS = [
    ("boy", "new", "男生新书榜", "male"),
    ("boy", "hot", "男生大热榜", "male"),
    ("boy", "over", "男生完结榜", "male"),
    ("boy", "collect", "男生收藏榜", "male"),
    ("girl", "new", "女生新书榜", "female"),
    ("girl", "hot", "女生大热榜", "female"),
    ("girl", "over", "女生完结榜", "female"),
    ("girl", "collect", "女生收藏榜", "female"),
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def parse_reads(rank_num, rank_unit):
    """拼接热度值: ('32.6', '万') -> '32.6万'。"""
    num = (rank_num or "").strip()
    unit = (rank_unit or "").strip()
    if not num:
        return "未知"
    return num + unit


def parse_book_item(li):
    """解析单个 <li class="rank-list-item"> 为 book dict。"""
    def text_of(selector, default=""):
        node = li.select_one(selector)
        return node.get_text(strip=True) if node else default

    # 详情链接 + 封面 + 排名
    link = li.select_one(".pic a[href*='/shuku/']")
    url = link["href"] if link and link.has_attr("href") else ""
    if url and url.startswith("/"):
        url = "https://www.qimao.com" + url
    img = li.select_one(".pic img")
    cover = img.get("src", "") if img else ""

    title = text_of("a.s-book-title") or "未知"

    # 作者: 作者页链接; 分类: shuku 筛选链接
    author = "未知"
    author_node = li.select_one(".s-book-info a[href*='/zuozhe/']")
    if author_node:
        author = author_node.get_text(strip=True)

    cat_nodes = li.select(".s-book-info a[href*='/shuku/a-']")
    category = " ".join(a.get_text(strip=True) for a in cat_nodes[:2])

    # 状态与字数: s-book-info 里的裸 em（连载中 / 49.02万字）
    ems = [e.get_text(strip=True) for e in li.select(".s-book-info em")]
    ems = [e for e in ems if e]
    status = next((e for e in ems if e in ("连载中", "已完结")), "")
    word_count = next((e for e in ems if e.endswith("字")), "")

    intro = text_of(".s-book-intro", "暂无简介")
    updated = text_of(".s-book-update em")

    # 热度值与升降
    reads = parse_reads(
        text_of(".rank-change-num .rank-num"),
        text_of(".rank-change-num .rank-unit"),
    )
    icon = li.select_one(".rank-change-num i.iconfont")
    change = ""
    if icon:
        classes = icon.get("class", [])
        change = "up" if "up" in classes else ("down" if "drop" in classes or "down" in classes else "")

    rank_tag = text_of(".rank-tag")

    book = {
        "title": title,
        "author": author,
        "reads": reads,
        "intro": intro,
        "cover": cover,
        "url": url,
    }
    # 附加字段（前端可选展示，趋势对比只用 url/reads/title）
    book["category"] = category
    book["status"] = status
    book["word_count"] = word_count
    book["updated_at"] = updated
    if change:
        book["change"] = change
    if rank_tag:
        book["rank_tag"] = rank_tag
    return book


def scrape_rank(session, channel, rank, name, channel_field, retries=3):
    """抓取单个榜单页，返回 (books, error)。"""
    url = f"https://www.qimao.com/paihang/{channel}/{rank}/date/"
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select("li.rank-list-item")
            if not items:
                raise ValueError(f"页面解析到 0 个条目（可能结构变更或被拦截）")
            books = [parse_book_item(li) for li in items]
            return books, None
        except Exception as e:
            print(f"  ⚠️  {name} 第 {attempt} 次失败: {e}")
            if attempt < retries:
                time.sleep(5 * attempt)
    return [], f"最终失败: {url}"


def run_scraper(sleep_sec=2):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(OUTPUT_DIR, f"qimao_ranks_{date_str}.json")

    session = requests.Session()
    all_categories = []
    failed = []

    for channel, rank, name, channel_field in RANKS:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 抓取 {name} ...")
        books, error = scrape_rank(session, channel, rank, name, channel_field)
        if error:
            failed.append(name)
            continue
        all_categories.append({
            "name": name,
            "channel": channel_field,
            "books": books,
        })
        # 每完成一个榜单立即写盘（防止中断丢数据）
        snapshot = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "categories": all_categories,
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        print(f"  ✅ {name}: {len(books)} 本")
        time.sleep(sleep_sec)

    if failed:
        print(f"\n⚠️  以下榜单抓取失败: {', '.join(failed)}")
        if not all_categories:
            raise SystemExit("所有榜单均抓取失败，退出码 1")

    print(f"\n✅ 抓取完成！共 {len(all_categories)} 个榜单，数据源：{output_file}")


if __name__ == "__main__":
    print("开始执行七猫小说榜单（男频+女频）抓取计划...")
    run_scraper(sleep_sec=2)
