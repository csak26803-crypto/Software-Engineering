# 1. 初期状態のデータ（学割、ペア割、家族割を追加）
CATALOG = {
    "T001": {"name": "大人チケット", "price": 2000, "desc": "18歳以上対象"},
    "T002": {"name": "子供チケット", "price": 1000, "desc": "小学生〜高校生対象"},
    "T003": {"name": "シニアチケット", "price": 1500, "desc": "65歳以上対象"},
    "T004": {"name": "学割チケット", "price": 1200, "desc": "大学生・専門学生対象（要学生証）"},
    "T005": {"name": "ペア割チケット", "price": 3600, "desc": "2名様分の価格（一括購入限定）"},
    "T006": {"name": "家族割チケット", "price": 5000, "desc": "大人2名＋子供2名のお得なセット"}
}


# 3. 並び替え機能を追加した表示関数（変更なし）
def display_catalog():
    print("=== 商品カタログ ===")
    
    # 辞書の中身を取り出し、ID(x[0])を小文字化(lower)した基準で並び替える(sorted)
    sorted_items = sorted(CATALOG.items(), key=lambda x: x[0].lower())
    
    for ticket_id, info in sorted_items:
        print(f"[{ticket_id}] {info['name']} - ¥{info['price']} ({info['desc']})")
    print("===================")

# 動作確認用
display_catalog()