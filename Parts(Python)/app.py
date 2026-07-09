import streamlit as st
import json
import os
import sys

# 画面のタイトル
st.title("🎟️ チケット購入 & QRコード生成システム")

# ------------------------------------------------------------------
# 【完璧な対策】元のファイルをテキストとしてUTF-8で強制的に読み込む
# ------------------------------------------------------------------
@st.cache_data
def load_catalog_safely():
    """元のファイルをUTF-8として安全に読み込み、CATALOG辞書を復元する"""
    catalog_path = "slice1_catalog.py"
    local_vars = {}
    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            code = f.read()
        # ファイル内の「CATALOG = {...}」の部分を実行して辞書を取得する
        exec(code, {}, local_vars)
        if "CATALOG" in local_vars:
            return local_vars["CATALOG"]
    except Exception:
        pass
    
    # 万が一読み込めなかった場合のバックアップ
    return {
        "T001": {"name": "大人チケット", "price": 2000, "desc": "18歳以上対象"},
        "T002": {"name": "子供チケット", "price": 1000, "desc": "小学生〜高校生対象"},
        "T003": {"name": "シニアチケット", "price": 1500, "desc": "65歳以上対象"},
        "T004": {"name": "学割チケット", "price": 1200, "desc": "大学生・専門学生対象（要学生証）"},
        "T005": {"name": "ペア割チケット", "price": 3600, "desc": "2名様分の価格（一括購入限定）"},
        "T006": {"name": "家族割チケット", "price": 5000, "desc": "大人2名＋子供2名のお得なセット"}
    }

# 安全に最新のカタログデータを取得
CATALOG = load_catalog_safely()

# ------------------------------------------------------------------
# セッション状態の初期化 (slice2_cartのクラスを使用)
# ------------------------------------------------------------------
try:
    from slice2_cart import Cart
except ImportError:
    class Cart:
        def __init__(self): self.items = []
        
        def add_item(self, tid, qty):
            # 既にカートに同じチケットがある場合は枚数を合算する
            for item in self.items:
                if item["ticket_id"] == tid:
                    item["quantity"] += qty
                    item["subtotal"] = item["price"] * item["quantity"]
                    return
            
            # まだカートにない場合は新規追加
            if tid in CATALOG:
                self.items.append({
                    "ticket_id": tid, 
                    "name": CATALOG[tid]["name"], 
                    "price": CATALOG[tid]["price"], 
                    "quantity": qty, 
                    "subtotal": CATALOG[tid]["price"] * qty
                })
                
        def update_quantity(self, index, new_qty):
            # 指定したインデックスの枚数を更新する
            if 0 <= index < len(self.items):
                item = self.items[index]
                item["quantity"] = new_qty
                item["subtotal"] = item["price"] * new_qty
                
        def remove_item(self, index):
            # 指定したインデックスのアイテムを削除する
            if 0 <= index < len(self.items):
                self.items.pop(index)
                
        def clear_cart(self): self.items = []
        def get_total(self): return sum(i["subtotal"] for i in self.items)
        def export_data(self): return json.dumps({"items": self.items, "total_amount": self.get_total()}, ensure_ascii=False)

if "cart" not in st.session_state:
    st.session_state.cart = Cart()

cart = st.session_state.cart

# ------------------------------------------------------------------
# 1. 商品カタログの表示
# ------------------------------------------------------------------
st.header("1. チケットを選択")

# カタログデータ（学割などが追加されても自動反映）から選択肢をループ生成
options = {}
for ticket_id, info in CATALOG.items():
    # 「大人チケット (¥2000) — 18歳以上対象」の形で綺麗に表示
    label = f"{info['name']} (¥{info['price']}) — {info['desc']}"
    options[label] = ticket_id

selected_ticket_name = st.selectbox("チケットの種類を選んでください", list(options.keys()))
selected_id = options[selected_ticket_name]

# 枚数選択
quantity = st.number_input("枚数", min_value=1, max_value=10, value=1)

# カートに追加ボタン
if st.button("🛒 カートに追加"):
    cart.add_item(selected_id, quantity)
    st.success(f"{CATALOG[selected_id]['name']} を {quantity} 枚追加しました！")

# ------------------------------------------------------------------
# 2. カートの中身表示
# ------------------------------------------------------------------
st.header("2. 現在のカート内容")

if not cart.items:
    st.info("カートは空です。")
else:
    # リストのインデックス(i)を取得するためにenumerateを使用
    for i, item in enumerate(cart.items):
        item_desc = CATALOG.get(item['ticket_id'], {}).get('desc', '')
        
        # 画面を3つのカラムに分割（商品情報 : 枚数変更 : 削除ボタン = 4 : 2 : 1 の比率）
        col1, col2, col3 = st.columns([4, 2, 1])
        
        with col1:
            st.write(f"・ **{item['name']}** — ¥{item['price']} 🏷️ *({item_desc})*")
            st.write(f" 小計: ¥{item['subtotal']}")
        
        with col2:
            # Streamlitの仕様上、ループ内で入力ウィジェットを出す場合は一意の key が必須
            new_qty = st.number_input(
                "枚数", 
                min_value=1, 
                max_value=20, # 必要に応じて上限を変更してください
                value=item['quantity'], 
                key=f"qty_{i}",
                label_visibility="collapsed"
            )
            # ユーザーが枚数を変更した瞬間に検知してカートを更新
            if new_qty != item['quantity']:
                cart.update_quantity(i, new_qty)
                st.rerun() # 画面を再描画して小計や合計金額を即時反映
                
        with col3:
            # 個別削除ボタン
            if st.button("❌", key=f"del_{i}"):
                cart.remove_item_by_index(i)
                st.rerun()
                
    st.write("---")
    st.metric(label="合計金額", value=f"¥{cart.get_total()}")

    if st.button("🗑️ カートを空にする"):
        cart.clear_cart()
        st.rerun()

# ------------------------------------------------------------------
# 3. 注文確定 & QRコード生成
# ------------------------------------------------------------------
st.header("3. 注文を確定してQRコードを発行")

if cart.items:
    if st.button("✨ 注文を確定する"):
        order_json = cart.export_data()
        
        try:
            from slice3_qrcode import generate_qr_from_json
            filename = "final_ticket_qr.png"
            generate_qr_from_json(order_json, filename)
            
            qr_path = os.path.join("QRcodefolder", filename)
            if os.path.exists(qr_path):
                st.success("🎉 注文が確定しました！QRコードを提示してください。")
                st.image(qr_path, caption="チケットQRコード", use_container_width=False)
        except Exception as e:
            st.error(f"QRコードの生成中にエラーが発生しました: {e}")