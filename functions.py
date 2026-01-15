import random
from math import radians, cos, sin, asin, sqrt, atan2, pi
import config


# расчет расстояния между двумя координатами
def haversine(lat1, lon1, lat2, lon2):
    R = 6372.8
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dLat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dLon / 2) ** 2
    c = 2 * asin(sqrt(a))
    Haversine = R * c * 1000  # переводим в метры

    return Haversine


# расчет азимута между двумя координатами
def bearing(lat1, lon1, lat2, lon2):
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    B = atan2((sin(dLon)) * cos(lat2),
              cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon))
    Bearing = B * 180 / pi
    if Bearing < 0:
        Bearing += 360
    return Bearing


# добавляет новую координату между двумя существующими
def multiply_coords(x: list) -> list:
    f = []

    for i in range(0, len(x) - 1):

        f.append(x[i])

        if i + 1 >= len(x):
            break

        lat1 = abs((x[i][0] + x[i + 1][0]) / 2)
        lon1 = abs((x[i][1] + x[i + 1][1]) / 2)

        f.append([lat1, lon1])

    f.append(x[-1])
    x = f

    return x


def random_speed(is_stop: bool) -> int:
    """
    Генерирует случайную скорость в км/ч
    Args:
        is_stop: True для остановки, False для движения
    Returns:
        int: скорость в км/ч (realistic для автобусов)
    """
    if is_stop:
        return random.randint(config.STOP_SPEED_MIN, config.STOP_SPEED_MAX)
    return random.randint(config.SPEED_MIN, config.SPEED_MAX)


def stop_find(route_coords: list[list[float]],
              bus_stop_coords: list[list[float]],
              allowed_distance: float = config.ALLOWED_DISTANCE) -> tuple[
    list[int], list[float]]:
    """
    Находит ближайшие точки маршрута к каждой остановке

    Args:
        route_coords: [[lat1, lon1], [lat2, lon2], ...]
        bus_stop_coords: [[stop_lat1, stop_lon1], ...]
        allowed_distance: max расстояние в метрах

    Returns:
        (stop_idx: [индексы в route_coords], distance_to: [дистанции])
    """
    stop_idx = []
    distance_to = []

    remaining_stops = bus_stop_coords.copy()  # Копируем для удаления

    for i, route_point in enumerate(route_coords):
        if not remaining_stops:  # Все остановки найдены
            break

        distances = [haversine(route_point[0], route_point[1],
                               stop[0], stop[1]) for stop in
                     remaining_stops]

        min_dist_idx = distances.index(min(distances))
        min_dist = distances[min_dist_idx]

        if min_dist <= allowed_distance:
            stop_idx.append(i)
            distance_to.append(min_dist)
            del remaining_stops[min_dist_idx]

    return stop_idx, distance_to
