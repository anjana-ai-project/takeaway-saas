from app.menu import get_menu, get_item_by_id


def test_get_menu_returns_list(capfd):
    """get_menu() must return a list so callers can iterate over items."""
    result = get_menu()
    print(f"\nTesting get_menu() type: expected list, got {type(result).__name__}")
    assert isinstance(result, list), (
        f"Expected get_menu() to return a list, got {type(result).__name__}"
    )


def test_menu_has_exactly_six_items(capfd):
    """Menu must contain exactly 6 items as defined in the data source."""
    result = get_menu()
    print(f"\nTesting menu length: expected 6, got {len(result)}")
    assert len(result) == 6, (
        f"Expected exactly 6 menu items, got {len(result)}"
    )


def test_each_item_has_required_keys(capfd):
    """Every menu item must expose id, name, category, and price fields."""
    required = {"id", "name", "category", "price"}
    for item in get_menu():
        missing = required - item.keys()
        print(f"\nChecking keys for item '{item.get('name', '?')}': missing={missing or 'none'}")
        assert not missing, (
            f"Menu item '{item.get('name')}' is missing required keys: {missing}"
        )


def test_all_prices_greater_than_zero(capfd):
    """Every menu item must have a positive price (no free or invalid items)."""
    for item in get_menu():
        print(f"\nChecking price for '{item['name']}': expected >0, got {item['price']}")
        assert item["price"] > 0, (
            f"Expected price > 0 for '{item['name']}', got {item['price']}"
        )


def test_get_item_by_id_returns_correct_item(capfd):
    """get_item_by_id() with a valid id must return the matching item."""
    item = get_item_by_id(1)
    print(f"\nLooking up item_id=1: got {item}")
    assert item is not None, "Expected a menu item for id=1, got None"
    assert item["id"] == 1, (
        f"Expected returned item to have id=1, got id={item['id']}"
    )


def test_get_item_by_id_returns_none_for_invalid_id(capfd):
    """get_item_by_id() with an id that does not exist must return None."""
    result = get_item_by_id(9999)
    print(f"\nLooking up item_id=9999: expected None, got {result}")
    assert result is None, (
        f"Expected None for non-existent id=9999, got {result}"
    )
