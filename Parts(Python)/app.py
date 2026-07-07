import streamlit as st
import json
import os

# 画面のタイトル
st.title("🎟️ チケット購入 & QRコード生成システム")

# ------------------------------------------------------------------
# 直接 CATALOG データを定義（文字化け・読み込み失敗対策）
# ------------------------------------------------------------------
CATALOG = {
    "T001": {"name": "大人チケット", "price": 2000, "desc": "18歳以上対象"},
    "T002": {"name": "子供チケット", "price": 1000, "desc": "小学生〜高校生対象"},
    "T003": {"name": "シニアチケット", "price": 1500, "desc": "65歳以上対象"}
}

# ------------------------------------------------------------------
# セッション状態の初期化
# ------------------------------------------------------------------
# Cartクラスのインポートでエラーが出ないよう安全に処理
try:
    from slice2_cart import Cart
except ImportError:
    # 万が一インポートに失敗した場合の簡易Cartクラス
    class Cart:
        def __init__(self): self.items = []
        def add_item(self, tid, qty):
            if tid in CATALOG:
                self.items.append({"ticket_id": tid, "name": CATALOG[tid]["name"], "price": CATALOG[tid]["price"], "quantity": qty, "subtotal": CATALOG[tid]["price"] * qty})
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

# 選択肢の文字を組み立て
options = {}
for ticket_id, info in CATALOG.items():
    # 「大人チケット (¥2000) [18歳以上対象]」 という見た目にする
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
    for item in cart.items:
        # 説明文をCATALOGから安全に取得
        item_desc = CATALOG.get(item['ticket_id'], {}).get('desc', '')
        st.write(f"・ **{item['name']}** x{item['quantity']} — ¥{item['subtotal']} 🏷️ *({item_desc})*")
    
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
        
        # QRコード生成関数の呼び出し
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