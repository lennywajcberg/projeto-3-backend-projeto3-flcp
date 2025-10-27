import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Favorite

ALLOWED_SYMBOLS = [
    "USD-BRL", "EUR-BRL", "GBP-BRL", "JPY-BRL", "CAD-BRL", "AUD-BRL",
    "CHF-BRL", "CNY-BRL", "ARS-BRL", "MXN-BRL",
    "BTC-BRL", "ETH-BRL", "BNB-BRL", "SOL-BRL", "DOGE-BRL", "XRP-BRL",
    "USD-EUR", "USD-JPY", "EUR-USD", "BTC-USD", "ETH-USD", "USD-GBP", 
]
AWESOME_BASE = "https://economia.awesomeapi.com.br"


def _client_id(request):
    """Return the client identifier sent in the X-Client-Id header."""
    cid = request.headers.get("X-Client-Id", "").strip()
    return cid or None


def _require_client_id(request):
    cid = _client_id(request)
    if not cid:
        return None, Response({"error": "missing_client_id"}, status=status.HTTP_400_BAD_REQUEST)
    return cid, None


@api_view(["GET"])
def symbols_view(request):
    """Return the catalog of supported currency/crypto pairs."""
    return Response({"symbols": ALLOWED_SYMBOLS})


@api_view(["GET"])
def quotes_view(request):
    """
    Return the latest quotes.

    Optional querystring: ?symbols=USD-BRL,EUR-BRL
    Optional header: X-Client-Id (marks favorites on the payload)
    """
    symbols_param = request.GET.get("symbols")
    if symbols_param:
        symbols = [s.strip() for s in symbols_param.split(",") if s.strip()]
    else:
        symbols = ALLOWED_SYMBOLS[:]

    symbols = [s for s in symbols if s in ALLOWED_SYMBOLS]
    if not symbols:
        return Response({"quotes": []})

    url = f"{AWESOME_BASE}/json/last/{','.join(symbols)}"
    try:
        upstream = requests.get(url, timeout=8)
        upstream.raise_for_status()
        data = upstream.json()
    except Exception as exc:
        return Response(
            {"error": "failed_upstream", "detail": str(exc)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    cid = _client_id(request)
    fav_set = set()
    if cid:
        favs = Favorite.objects.filter(client_id=cid, symbol__in=symbols).values_list("symbol", flat=True)
        fav_set = set(favs)

    def to_float(value):
        try:
            return float(value)
        except Exception:
            return None

    quotes = []
    for sym in symbols:
        key = sym.replace("-", "")
        raw = data.get(key)
        if not raw:
            continue

        price = to_float(raw.get("bid") or raw.get("ask") or raw.get("price"))
        change_pct = to_float(raw.get("pctChange"))
        updated_at = raw.get("create_date") or raw.get("timestamp") or raw.get("createDate")

        quotes.append(
            {
                "symbol": sym,
                "price": price,
                "changePct": change_pct,
                "updatedAt": str(updated_at) if updated_at is not None else None,
                "isFavorite": sym in fav_set,
            }
        )

    return Response({"quotes": quotes})


@api_view(["GET", "POST"])
def favorites_collection_view(request):
    """
    GET -> return the list of favorite symbols for the client.
    POST -> create a new favorite.
    """
    cid, error_response = _require_client_id(request)
    if error_response:
        return error_response

    if request.method == "GET":
        favs = Favorite.objects.filter(client_id=cid).values_list("symbol", flat=True)
        return Response({"favorites": list(favs)})

    symbol = (request.data or {}).get("symbol", "").strip()
    if symbol not in ALLOWED_SYMBOLS:
        return Response({"error": "invalid_symbol"}, status=status.HTTP_400_BAD_REQUEST)

    favorite, created = Favorite.objects.get_or_create(client_id=cid, symbol=symbol)
    status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return Response({"symbol": favorite.symbol, "favorited": True}, status=status_code)


@api_view(["DELETE"])
def favorite_detail_view(request, symbol):
    """Remove a favorite from the client collection."""
    cid, error_response = _require_client_id(request)
    if error_response:
        return error_response

    symbol = symbol.strip()
    if symbol not in ALLOWED_SYMBOLS:
        return Response({"error": "invalid_symbol"}, status=status.HTTP_400_BAD_REQUEST)

    deleted, _ = Favorite.objects.filter(client_id=cid, symbol=symbol).delete()
    if not deleted:
        return Response({"error": "favorite_not_found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_204_NO_CONTENT)
