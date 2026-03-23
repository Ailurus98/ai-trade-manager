from .stocks import STOCKS


def search_stock(query):
    results = {}

    for name, symbol in STOCKS.items():
        if query.lower() in name.lower():
            results[name] = symbol

    return results
