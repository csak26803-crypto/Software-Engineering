# 1. 初期状態のデータ
CATALOG = {
    "T001": {"name": "大人チケット", "price": 2000, "desc": "18歳以上対象"},
    "T002": {"name": "子供チケット", "price": 1000, "desc": "小学生〜高校生対象"},
    "T003": {"name": "シニアチケット", "price": 1500, "desc": "65歳以上対象"}
}

# 2. 【ここがポイント！】大文字のデータを自動的に小文字のIDにも紐付け（同期）します
CATALOG["t001"] = CATALOG["T001"]
CATALOG["t002"] = CATALOG["T002"]
CATALOG["t003"] = CATALOG["T003"]

# 3. 並び替え機能を追加した表示関数
def display_catalog():
    print("=== 商品カタログ ===")
    
    # 辞書の中身を取り出し、ID(x[0])を小文字化(lower)した基準で並び替える(sorted)
    sorted_items = sorted(CATALOG.items(), key=lambda x: x[0].lower())
    
    for ticket_id, info in sorted_items:
        print(f"[{ticket_id}] {info['name']} - ¥{info['price']} ({info['desc']})")
    print("===================")