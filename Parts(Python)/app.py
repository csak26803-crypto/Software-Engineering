import streamlit as st
import json
import os
from slice1_catalog import CATALOG
from slice2_cart import Cart
from slice3_qrcode import generate_qr_from_json

# 画面のタイトル
st.title("🎟️ チケット購入 & QRコード生成システム")

if "cart" not in st.session_state:
    st.session_state.cart = Cart()

cart = st.session_state.cart

# ------------------------------------------------------------------
# 1. 商品カタログの表示
# ------------------------------------------------------------------
st.header("1. チケットを選択")

# 💡 選択肢の表示を 「名前 (価格) - 説明文」 に変更しました！
options = {f"{info['name']} (¥{info['price']}) — {info['desc']}": ticket_id for ticket_id, info in CATALOG.items()}
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
    # 💡 カート内にも説明文（desc）を表示するようにしました
    for item in cart.items:
        # CATALOGから説明文を引っ張ってくる
        item_desc = CATALOG[item['ticket_id']]['desc']
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
        
        filename = "final_ticket_qr.png"
        generate_qr_from_json(order_json, filename)
        
        qr_path = os.path.join("QRcodefolder", filename)
        if os.path.exists(qr_path):
            st.success("🎉 注文が確定しました！QRコードを提示してください。")
            st.image(qr_path, caption="チケットQRコード", use_container_width=False)
