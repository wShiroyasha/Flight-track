from datetime import date, datetime
from collections import Counter
from unicodedata import normalize

import serpapi
import airportsdata

from ..config import settings


_AIRPORTS = airportsdata.load("IATA")


def _location_id(location: str) -> str:
	
	clean_location = " ".join(location.split())
	location_key = normalize("NFKD", clean_location).encode("ascii", "ignore").decode().casefold()

	if len(clean_location) == 3 and clean_location.upper() in _AIRPORTS:
		return clean_location.upper()

	matching_airports = [
		(airport_id, airport)
		for airport_id, airport in _AIRPORTS.items()
		if normalize("NFKD", airport["city"])
		.encode("ascii", "ignore")
		.decode()
		.casefold()
		== location_key
	]
	if not matching_airports:
		raise LookupError(f"No airports found for city: {clean_location}")

	country = Counter(airport["country"] for _, airport in matching_airports).most_common(1)[0][0]
	airport_ids = [
		airport_id for airport_id, airport in matching_airports if airport["country"] == country
	]
	return ",".join(sorted(airport_ids))


def _parse_datetime(value: str) -> datetime:
	return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _offer_legs(offer: dict) -> tuple[datetime, datetime]:
	legs = offer.get("flights") or []
	if not legs:
		raise LookupError("The flight provider returned no itinerary")

	return (
		_parse_datetime(legs[0]["departure_airport"]["time"]),
		_parse_datetime(legs[-1]["arrival_airport"]["time"]),
	)


def _provider_error_message(error: serpapi.HTTPError) -> str:
	response = getattr(error, "args", [None])[0]
	response = getattr(response, "response", None)
	if response is not None:
		try:
			message = response.json().get("error")
			if message:
				return str(message)
		except ValueError:
			pass
	return str(error)


def search_flight(
	origin: str,
	destination: str,
	departure_date: date,
	return_date: date | None,
) -> dict:
	if not settings.serpapi_key:
		raise RuntimeError("SERPAPI_KEY is not configured")

	params = {
		"engine": "google_flights",
		"departure_id": _location_id(origin),
		"arrival_id": _location_id(destination),
		"outbound_date": departure_date.isoformat(),
		"currency": "USD",
		"adults": 1,
	}
	if return_date:
		params["return_date"] = return_date.isoformat()

	client = serpapi.Client(api_key=settings.serpapi_key)
	try:
		results = client.search(params)
	except serpapi.HTTPError as error:
		raise LookupError(
			f"The flight provider rejected the search: {_provider_error_message(error)}"
		) from error
	offers = results.get("best_flights") or results.get("other_flights") or []
	if not offers:
		raise LookupError("No flights were found")

	offer = offers[0]
	outbound_departure, outbound_arrival = _offer_legs(offer)
	return_departure = None
	return_arrival = None
	if return_date:
		departure_token = offer.get("departure_token")
		if not departure_token:
			raise LookupError("The flight provider returned no return itinerary")

		try:
			return_results = client.search(
				{
					"engine": "google_flights",
					"departure_token": departure_token,
				}
			)
		except serpapi.HTTPError as error:
			try:
				return_results = client.search(
					{
						"engine": "google_flights",
						"departure_id": _location_id(destination),
						"arrival_id": _location_id(origin),
						"outbound_date": return_date.isoformat(),
						"type": 2,
						"currency": "USD",
						"adults": 1,
					}
				)
			except serpapi.HTTPError as fallback_error:
				raise LookupError(
					"The flight provider rejected the return itinerary: "
					f"{_provider_error_message(fallback_error)}"
				) from fallback_error

		return_offers = (
			return_results.get("best_flights")
			or return_results.get("other_flights")
			or []
		)
		if not return_offers:
			raise LookupError("No return flights were found")
		return_departure, return_arrival = _offer_legs(return_offers[0])

	return {
		"original_price": float(offer["price"]),
		"current_price": float(offer["price"]),
		"outbound_departure": outbound_departure,
		"outbound_arrival": outbound_arrival,
		"return_departure": return_departure,
		"return_arrival": return_arrival,
	}
