from decimal import Decimal

from app.ingestion.product_importer import map_product_row, parse_list_cell


def test_parse_list_cell_supports_chinese_separators() -> None:
    assert parse_list_cell("气虚质、阳虚质，平和质") == ["气虚质", "阳虚质", "平和质"]


def test_map_product_row_normalizes_form_and_price() -> None:
    row = {
        "商品名称": "黄芪红枣茶",
        "品类": "养生花茶",
        "形态": "袋泡茶",
        "售价": "￥39.9",
        "适用体质": "气虚质、阳虚质",
        "原料": "黄芪，红枣",
    }
    mapping = {
        "name": "商品名称",
        "category": "品类",
        "form": "形态",
        "price": "售价",
        "constitutions": "适用体质",
        "ingredients": "原料",
    }

    product = map_product_row(row, mapping)

    assert product.form == "茶饮"
    assert product.price == Decimal("39.9")
    assert product.constitutions == ["气虚质", "阳虚质"]
    assert product.ingredients == ["黄芪", "红枣"]


def test_map_product_row_supports_multiple_header_candidates() -> None:
    row = {
        "__sheet_name": "方圆荟",
        "产品品名": "杜仲雄花茶",
        "功效": "补肾固精",
        "适用于体质": "1. 肾阳虚 / 阳虚质（较适宜）\n2. 气虚质",
    }
    mapping = {
        "name": ["产品名称", "产品品名"],
        "form": "__sheet_name",
        "description": ["卖点", "功效"],
        "constitutions": ["适用体质", "适用于体质"],
    }

    product = map_product_row(row, mapping)

    assert product.name == "杜仲雄花茶"
    assert product.form == "方圆荟"
    assert product.constitutions == ["气虚质", "阳虚质"]


def test_map_product_row_keeps_unknown_constitutions() -> None:
    row = {"产品名称": "大枣", "适用体质": "1. 气虚体质\n2. 血虚体质"}
    mapping = {"name": "产品名称", "constitutions": "适用体质"}

    product = map_product_row(row, mapping)

    assert product.constitutions == ["气虚质"]
    assert product.unknown_constitutions == ["血虚体质"]
