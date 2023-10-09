import asyncio


async def main(
    start_req_num: int,
    step: int,
    seconds: int
) -> None:
    req_num = start_req_num
    for s in range(seconds):
        for i in range(req_num):
            # нужно сохранять результат
            await test_terminal()
            await test_mobile_app_endpoins()
        
        req_num += step
        await asyncio.sleep(1)


async def test_terminal() -> dict:
    """
    Функция для тестирования запросов к терминалу,
    возвращает словарь с кодами ответов, например:
    {200: 54, 404: 23}
    """
    result: dict = {}

    # тело функции

    return result


async def test_mobile_app_endpoins() -> dict:
    """
    Функция для тестирования запросов,
    связанных с мобильным приложение,
    возвращает словарь с кодами ответов,
    например: {200: 54, 404: 23}
    """
    result: dict = {}

    # тело функции

    return result

    
if __name__ == '__main__':
    asyncio.run(main(10, 10, 100))