MENU_ITEMS = [
    {"id": 1, "name": "Classic Beef Burger", "category": "Burgers", "price": 199},
    {"id": 2, "name": "Spicy Chicken Burger", "category": "Burgers", "price": 179},
    {"id": 3, "name": "Veggie Delight Burger", "category": "Burgers", "price": 149},
    {"id": 4, "name": "Masala Fries", "category": "Sides", "price": 89},
    {"id": 5, "name": "Onion Rings", "category": "Sides", "price": 79},
    {"id": 6, "name": "Mango Shake", "category": "Drinks", "price": 99},
]


# Returns the full list of menu items available for ordering.
def get_menu():
    return MENU_ITEMS


# Returns a single menu item matching item_id, or None if not found.
def get_item_by_id(item_id: int):
    return next((item for item in MENU_ITEMS if item["id"] == item_id), None)
