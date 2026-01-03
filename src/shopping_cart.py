from typing import List

class ShoppingCart:
	def __init__(self) -> None:
		self.items: List[str] = []
		self.max_size: int = 5

	def add(self, item: str):
		if self.size() == self.max_size:
			raise OverflowError("Cart is full - cannot add more")
		self.items.append(item)

	def size(self) -> int:
		return len(self.items)

	def get_items(self) -> List[str] | None:
		return self.items

	def get_total_price(self, price_dict):
		total_price = 0
		for item in self.items:
			total_price += price_dict.get(item)
		return total_price
