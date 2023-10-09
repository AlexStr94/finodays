import asyncio
from tests.statistics import Statistics


async def main(
        start_req_num: int,
        step: int,
        seconds: int
) -> Statistics:
    statistics = Statistics()
    req_num = start_req_num

    for s in range(seconds):
        for i in range(req_num):
            await test_terminal(statistics, req_num)
            await test_mobile_app_endpoins(statistics, req_num)

        req_num += step
        await asyncio.sleep(1)

    return statistics


async def test_terminal(statistics: Statistics, req_num: int) -> None:
    """
    Функция для тестирования запросов к терминалу
    """

    # Код запроса
    ...

    # Записать статистику по запросу
    # Так выглядит вход:
    # add(self, endpoint_name: str, frequency: int, response_code: int, response_time: float) -> None:
    # Ниже раскомментить для работы
    # statistics.add(endpoint_name='*имя эндпоинта*', req_num, '*код ответа*', '*время ответа*')


async def test_mobile_app_endpoins(statistics: Statistics, req_num: int) -> None:
    """
    Функция для тестирования запросов,
    связанных с мобильным приложением
    """

    # Код запроса
    ...

    # Записать статистику по запросу
    # Так выглядит вход:
    # add(self, endpoint_name: str, frequency: int, response_code: int, response_time: float) -> None:
    # Ниже раскомментить для работы
    # statistics.add(endpoint_name='*имя эндпоинта*', req_num, '*код ответа*', '*время ответа*')


if __name__ == '__main__':
    final_statistics = asyncio.run(main(10, 10, 100))
    final_statistics.save_all_to_csv('tests/files')
