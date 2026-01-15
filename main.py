import datetime as dt
from api_itec import request_itec, get_data, get_coord_bus_stop, \
    gen_curl_create_timemachine
from functions import *
import config
from logger import setup_logger

logger = setup_logger()


def generate_navigation_sql() -> None:
    """Генерирует query.txt"""
    # Получение данных
    routes_data = request_itec("getRegularRoutes")
    route_coords, _, devices, _ = get_data(routes_data, config.FLIGHT_ID)
    bus_stop_coords = get_coord_bus_stop()
    if len(route_coords) == 0:
        return logger.info("Координаты маршрута не найдены или отсутствуют")
    else:
        # Мультипликация координат
        route_coords = multiply_coords(route_coords)

    # Поиск остановок
    stop_idx, distance_to = stop_find(route_coords, bus_stop_coords,
                                      config.ALLOWED_DISTANCE)

    # Генерация SQL
    query = []
    time_start = None
    time_end = None
    config.START_TIME = int(config.START_TIME)
    if len(routes_data["result"]["routes"]) == 0:
        return logger.info("Маршруты в ITEC не найдены")
    else:
        for i in range(len(route_coords) - 1):
            lat, lon = route_coords[i]
            lat_next, lon_next = route_coords[i + 1]

            distance = haversine(lat, lon, lat_next, lon_next)
            azimuth = int(calc_azimuth(lat, lon, lat_next, lon_next))
            speed_kmh = random_speed(i in stop_idx)

            timestamp = dt.datetime.fromtimestamp(config.START_TIME)

            sql = f"""INSERT INTO {config.TABLE_NAME}
    (sid, grz, create_timestamp, navi_timestamp, longitude, latitude, course, speed, ip_source, ip_destination, history)
    VALUES('{devices[0]}', '{config.GRZ}', '{timestamp}', '{timestamp}', {lon}, {lat}, {azimuth}, {speed_kmh}, '192.168.32.125', '192.168.32.67:20058', '0');"""

            query.append(sql)
            # Обновление времени
            if i in stop_idx and speed_kmh == 0:
                # Если остановка
                config.START_TIME += config.BUS_STOP_TIME
            else:
                # Если движение
                speed_ms = speed_kmh / 3.6
                config.START_TIME += distance / speed_ms

            if i == 0:
                time_start = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            if i == len(route_coords) - 2:
                time_end = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Запись
        with open('query.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(query))

        # Статистика
        logger.info(f'Всего координат маршрута: {len(route_coords)}')
        logger.info(f'Остановки: {len(stop_idx)} шт. на индексах {stop_idx}')
        logger.info(
            f'Дистанции от остановок: {[f"{d:.1f}м" for d in distance_to]}')
        logger.info(
            gen_curl_create_timemachine(devices[0], start_time=time_start,
                                        end_time=time_end))


if __name__ == "__main__":
    generate_navigation_sql()
