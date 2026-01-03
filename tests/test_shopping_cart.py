import pytest
from shopping_cart import ShoppingCart

@pytest.fixture()
def new_cart():
	return ShoppingCart()

def test_can_add_item_to_cart(new_cart):
	new_cart.add("apple")
	assert new_cart.size() == 1

def test_added_item_exists(new_cart):
	new_cart.add("rice")
	assert "rice" in [x.lower() for x in new_cart.get_items()]

def test_cart_full(new_cart):
	for _ in range(5):
		new_cart.add("something")
	with pytest.raises(OverflowError):
		new_cart.add("coffee")

def test_get_total_price(new_cart):
	new_cart.add("water")
	new_cart.add("coffee")
	new_cart.add("milk")
	prices = {"water": 1, "coffee": 3, "milk": 2}
	assert new_cart.get_total_price(price_dict=prices) == 6
