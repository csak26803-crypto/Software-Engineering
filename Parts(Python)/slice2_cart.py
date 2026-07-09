# slice2_cart.py
import json
from slice1_catalog import CATALOG, display_catalog

class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, ticket_id, quantity, option="なし"):
        """【入力・処理】商品をカートに追加し、小計を計算する"""
        if ticket_id in CATALOG:
            ticket = CATALOG[ticket_id]
            subtotal = ticket["price"] * quantity
            self.items.append({
                "ticket_id": ticket_id,
                "name": ticket["name"],
                "price": ticket["price"],
                "quantity": quantity,
                "option": option,
                "subtotal": subtotal
            })
            print(f" -> {ticket['name']}を{quantity}枚追加しました。（小計: ¥{subtotal}）")
        else:
            print(f"エラー: 商品ID '{ticket_id}' は存在しません。")

    # ▼▼▼【Streamlit用に新しく追記するメソッド 1】▼▼▼
    def update_quantity(self, index, new_qty):
        """指定したインデックス（〇番目）の枚数と小計を直接更新する"""
        if 0 <= index < len(self.items):
            item = self.items[index]
            item["quantity"] = new_qty
            item["subtotal"] = item["price"] * new_qty
            print(f" -> {item['name']}の枚数を {new_qty} 枚に変更しました。")

    # ▼▼▼【Streamlit用に新しく追記するメソッド 2】▼▼▼
    def remove_item_by_index(self, index):
        """指定したインデックス（〇番目）のアイテムを完全に削除する"""
        if 0 <= index < len(self.items):
            removed = self.items.pop(index)
            print(f" -> {removed['name']}をカートから削除しました。")

    def remove_item(self, ticket_id, quantity):
        """【追加機能】指定した商品IDの数量を、任意の数だけ減らす（CUI用）"""
        # ... (既存のコードのまま変更なし) ...
        for item in self.items:
            if item["ticket_id"] == ticket_id:
                if item["quantity"] > quantity:
                    item["quantity"] -= quantity
                    item["subtotal"] = item["price"] * item["quantity"]
                    print(f" -> {item['name']}を{quantity}枚減らしました。")
                else:
                    self.items.remove(item)
                    print(f" -> {item['name']}がカートから完全になくなりました。")
                return
        print(f"エラー: カート内に商品ID '{ticket_id}' は見つかりません。")

    def clear_cart(self):
        """【追加機能】カートの中身をすべて空にする"""
        self.items = []
        print(" -> カートの中身をすべてクリアしました。")

    def get_total(self):
        """【処理】カート内の合計金額を計算する"""
        return sum(item["subtotal"] for item in self.items)

    def display_cart(self):
        """【表示】現在のカートの中身と合計金額を表示する"""
        print("\n=== 現在のカート内容 ===")
        if not self.items:
            print("カートは空です。")
            return
        
        for i, item in enumerate(self.items, 1):
            print(f"{i}. {item['name']} x{item['quantity']} (OP:{item['option']}) - ¥{item['subtotal']}")
        print(f"【合計金額】: ¥{self.get_total()}")
        print("========================\n")

    def export_data(self):
        """【保存用のデータ出力】カート状態をJSON文字列に変換する"""
        data = {
            "items": self.items,
            "total_amount": self.get_total()
        }
        return json.dumps(data, ensure_ascii=False)
        
cart = Cart()

if __name__ == "__main__":
    display_catalog()  