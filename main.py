import datetime as dt
import time
from api_itec import request_itec, get_data, get_bus_stop, \
    gen_curl_create_timemachine
from functions import *
import config
from interact_menu import interactive_route_select
from logger import setup_logger

logger = setup_logger()


def generate_navigation_sql() -> None:
    """Генерирует query.txt"""
    # Получение данных
    routes_data = request_itec("getRegularRoutes")

    if len(routes_data["result"]["routes"]) == 0:
        return logger.info("Маршруты в ITEC не найдены")

    selected_route_id, selected_flight_id = interactive_route_select(
        routes_data)
    if not selected_flight_id:
        return logger.info("Выбор отменен")

    # Получаем данные выбранного рейса
    route_coords, _, devices, routes_map = get_data(routes_data,
                                                    selected_flight_id)

    if len(route_coords) == 0:
        return logger.info("Координаты маршрута не найдены")

    # Получаем остановки для выбранного рейса
    bus_stop_coords, bus_stop_names = get_bus_stop(selected_flight_id)

    # Мультипликация координат
    route_coords = multiply_coords(route_coords)

    # Поиск остановок
    stop_idx, distance_to = stop_find(route_coords, bus_stop_coords,
                                      config.ALLOWED_DISTANCE)

    # Генерация SQL
    query = []
    time_start = None
    time_end = None
    start_time = int(time.time())

    for i in range(len(route_coords) - 1):
        lat, lon = route_coords[i]
        lat_next, lon_next = route_coords[i + 1]

        distance = haversine(lat, lon, lat_next, lon_next)
        azimuth = int(calc_azimuth(lat, lon, lat_next, lon_next))
        speed_kmh = random_speed(i in stop_idx)
        timestamp_utc = dt.datetime.fromtimestamp(start_time, dt.timezone.utc)
        navi_timestamp = timestamp_utc.strftime('%Y-%m-%d %H:%M:%S.%f')

        sql = f"""INSERT INTO {config.TABLE_NAME}
    (sid, grz, create_timestamp, navi_timestamp, longitude, latitude, course, speed, ip_source, ip_destination, history)
    VALUES('{devices[0]}', '{config.GRZ}', '{navi_timestamp}', '{navi_timestamp}', {lon}, {lat}, {azimuth}, {speed_kmh}, '192.168.32.125', '192.168.32.67:20058', '0');"""

        query.append(sql)

        # Обновление времени
        if i in stop_idx and speed_kmh == 0:
            # Если остановка
            start_time += config.BUS_STOP_TIME
        else:
            # Если движение
            speed_ms = speed_kmh / 3.6
            start_time += distance / speed_ms

        if i == 0:
            time_start = timestamp_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        if i == len(route_coords) - 2:
            time_end = timestamp_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Запись и статистика
    with open('query.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(query))

    logger.info(f'Маршрут: {routes_map.get(selected_route_id, "Неизвестно")}')
    logger.info(f'Всего координат маршрута: {len(route_coords)}')
    logger.info(f'Остановки: {len(stop_idx)} шт. на индексах {stop_idx}')
    logger.info(
        f'Дистанции от остановок: {[f"{d:.1f}м" for d in distance_to]}')
    logger.info(
        gen_curl_create_timemachine(devices[0], start_time=time_start,
                                    end_time=time_end))


if __name__ == "__main__":
    generate_navigation_sql()
