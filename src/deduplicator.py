# Simple but important. Separates thoughtful engineering from a naive demo.

def deduplicate(
    candidates: list[dict],
    purchase_history: list[str],
    owned_products: list[dict]   # full product objects for incompatibility check
) -> list[dict]:

    # Build incompatibility set from all owned products
    incompatible_ids = set()
    for owned in owned_products:
        for inc_id in owned.get('incompatible_with', []):
            incompatible_ids.add(inc_id)

    filtered = []
    for candidate in candidates:
        pid = candidate['product_id']
        if pid in purchase_history:
            continue     # already owns it
        if pid in incompatible_ids:
            continue     # incompatible with something she owns
        filtered.append(candidate)

    return filtered


if __name__ == "__main__":
    # Unit test 1: owned product excluded
    candidates = [
        {'product_id': 'MW-001', 'name_en': 'Weaning Set', 'incompatible_with': []},
        {'product_id': 'MW-002', 'name_en': 'Feeding Spoons', 'incompatible_with': []},
        {'product_id': 'MW-003', 'name_en': 'Weaning Bowls', 'incompatible_with': []},
    ]
    result = deduplicate(candidates, purchase_history=['MW-001'], owned_products=[])
    assert len(result) == 2
    assert all(p['product_id'] != 'MW-001' for p in result)
    print("Test 1 (owned excluded): PASS")

    # Unit test 2: incompatible product excluded
    candidates2 = [
        {'product_id': 'MW-009', 'name_en': 'Infant Car Seat'},
        {'product_id': 'MW-010', 'name_en': 'Forward Car Seat'},
        {'product_id': 'MW-011', 'name_en': 'Joie i-Spin'},
    ]
    owned = [{'product_id': 'MW-009', 'incompatible_with': ['MW-010']}]
    result2 = deduplicate(candidates2, purchase_history=['MW-009'], owned_products=owned)
    assert len(result2) == 1
    assert result2[0]['product_id'] == 'MW-011'
    print("Test 2 (incompatible excluded): PASS")

    # Unit test 3: clean candidate passes through
    candidates3 = [{'product_id': 'MW-030', 'name_en': 'Play Mat'}]
    result3 = deduplicate(candidates3, purchase_history=[], owned_products=[])
    assert len(result3) == 1
    print("Test 3 (clean candidate): PASS")

    # Unit test 4: all excluded → empty list
    result4 = deduplicate(candidates, purchase_history=['MW-001','MW-002','MW-003'], owned_products=[])
    assert result4 == []
    print("Test 4 (all excluded): PASS")

    print("All deduplicator tests passed ✓")
