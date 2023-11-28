from pydantic import BaseModel, root_validator


class Item(BaseModel):
    id: int
    name: str
    # priceU: float
    salePriceU: float
    brand: str
    sale: int
    rating: float
    volume: int

    @root_validator(pre=True)
    def convert_sale_price(cls, values: dict):
        item_name = values.get("name")
        # price = values.get("priceU")
        sale_price = values.get("salePriceU")
        values["name"] = item_name.replace(',', ';')
        if sale_price is not None:
            # values["priceU"] = price / 100
            values["salePriceU"] = sale_price / 100
        return values


class Items(BaseModel):
    products: list[Item]
