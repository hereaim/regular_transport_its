import requests
import config
import shlex, json
from logger import setup_logger

logger = setup_logger()


def request_itec(command: str, stops: list | None = None) -> dict:
    payload = {"auth_token": f"{config.TOKEN}", "id": "1",
               "command": command}
    if stops:
        payload["stops"] = stops
    response = requests.post(config.URL_ITEC, json=payload)
    return response.json()


def get_data(data: dict, flight_id: str = None):
    route_coords = []
    bus_stop_id = []
    devices = []
    routes_map: dict[str, str] = {}

    if "command" in data and data["command"] == "getBusStops":
        if "stops" in data:
            bus_stop_id = [stop["id"] if isinstance(stop, dict) else stop for
                           stop in data["stops"]]
        return route_coords, bus_stop_id

    if "result" in data and "routes" in data["result"]:
        for route in data["result"]["routes"]:
            rn = route.get("routeNumber", "Неизвестно")
            rid = route.get("id")
            if rid is not None:
                routes_map[rid] = rn

            for flight in route.get("flights", []):
                if flight.get("id") == flight_id:
                    route_coords.extend(flight.get("coordinates", []))
                    stops = flight.get("stops", [])
                    bus_stop_id = [
                        stop["id"] if isinstance(stop, dict) else stop for stop
                        in stops]
                    devices = flight.get("devices", [])
                    return route_coords, bus_stop_id, devices, routes_map
    return route_coords, bus_stop_id, devices, routes_map


def get_coord_bus_stop() -> list[list[float]]:
    """Получает координаты bus stops для flight_id"""
    # Шаг 1: Получить routes и bus_stop_id
    routes_data = request_itec("getRegularRoutes")
    _, bus_stop_id, _, _ = get_data(routes_data,
                                    flight_id=config.FLIGHT_ID)

    # Шаг 2: Запросить детали stops
    stops_data = request_itec("getBusStops", stops=bus_stop_id)
    coords = []
    stops_dict = stops_data.get("result", {}).get("stops", {})

    for stop_id, stop_info in stops_dict.items():
        lat = stop_info.get("latitude")
        lon = stop_info.get("longitude")
        if lat is not None and lon is not None:
            coords.append(
                [float(lat), float(lon)])  # float для haversine/bearing

    return coords


def gen_curl_create_timemachine(devices: list[dict], start_time: str,
                                end_time: str) -> str:
    """Генерирует curl для создания TimeMachine"""
    payload = {
        "command": "createTimeMachine",
        "timeMachine": f"{devices}",
        "naviTimeStart": f"{start_time}",
        "naviTimeEnd": f"{end_time}",
        "original": f"{devices}",
        "gapDivider": 1,
        "repeatSecs": 5,
        "auth_token": f"{config.TOKEN}"
    }
    json_str = json.dumps(payload)
    curl_cmd = (
        f"curl --location '{config.URL_ITEC}' "
        f"--header 'Content-Type: application/json' "
        f"--data {shlex.quote(json_str)}"
    )
    return curl_cmd
