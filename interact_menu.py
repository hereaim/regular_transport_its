from api_itec import get_data, get_bus_stop
from logger import setup_logger

logger = setup_logger()


def print_routes_menu(routes_map: dict[str, str]):
    print("\nВыберите маршрут:")
    print("-" * 60)
    for i, (route_id, route_num) in enumerate(routes_map.items(), 1):
        print(f"{i:2d}. {route_num:<10} | ID: {route_id}")
    print(" 0. Выход")
    print("-" * 60)


def print_flights_menu(flights: list[dict], flight_stops: dict[str, tuple[str, str]]):
    print("\nВыберите рейс:")
    print("-" * 40)
    for i, flight in enumerate(flights, 1):
        fid = flight.get("id", "Неизвестно")[:8] + "..."
        if flight_stops and flight.get("id") in flight_stops:
            start_name, end_name = flight_stops[flight["id"]]
            stops_info = f"От:'{start_name}' - До:'{end_name}'"

        print(f"{i:2d}. {fid:<10} {stops_info}")
    print("-" * 40)


def interactive_route_select(routes_data: dict):
    """Выбор маршрута и рейса"""
    _, _, _, routes_map = get_data(routes_data)  # Получаем все маршруты

    if not routes_map:
        logger.error("Маршруты не найдены")
        return None, None

    # Показываем маршруты
    print_routes_menu(routes_map)

    try:
        route_choice = int(
            input("Выберите номер маршрута (или 0 для выхода): ")) - 1
        if route_choice < 0:
            return None, None

        selected_route_id = list(routes_map.keys())[route_choice]
        selected_route_num = routes_map[selected_route_id]

        # Получаем рейсы маршрута
        selected_route = next(r for r in routes_data["result"]["routes"] if
                              r["id"] == selected_route_id)
        flights = selected_route.get("flights", [])

        if not flights:
            logger.warning(f"Рейсы для {selected_route_num} не найдены")
            return None, None

        # Загружаем названия остановок для всех рейсов маршрута
        flight_stops = {}
        for flight in flights:
            flight_id = flight.get("id")
            if flight_id:
                _, (start_name, end_name) = get_bus_stop(flight_id)
                flight_stops[flight_id] = (start_name, end_name)

        # Показываем рейсы
        print_flights_menu(flights, flight_stops)

        flight_choice = int(input("Выберите номер рейса: ")) - 1
        selected_flight_id = flights[flight_choice]["id"]

        print(
            f"\nВыбран маршрут: {selected_route_num}. Рейс: {selected_flight_id}")
        return selected_route_id, selected_flight_id

    except (ValueError, IndexError) as e:
        logger.error(f"Неверный выбор: {e}")
        return None, None
