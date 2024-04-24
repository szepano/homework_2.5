import platform

import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta


async def gather_dates(days: int, today=datetime.now().date()):
    dates_raw = [today]
    one_day = timedelta(days=1)
    for i in range(1, days):
        today -= one_day
    dates_raw.append(today)
    return dates_raw

def string_dates(dates_raw):
    dates_final = [i.strftime('%Y-%m-%d') for i in dates_raw]
    return(dates_final)
        
def get_urls(dates_final, codes=('USD', 'EUR')):
    urls = []
    for code in codes:
        urls.append(f'https://api.nbp.pl/api/exchangerates/rates/c/{code}/{dates_final[1]}/{dates_final[0]}?format=json')
    return urls


async def exchange(urls):
    result = []
    exchange_dict = {}
    for url in urls:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    result.append(f'Something went wrong, probably non-working day, status: {response.status}')
                    continue
                data = await response.json()
                rates = data['rates']
                code = data['code']
                for i in rates:
                    exchange_dict.update({i['effectiveDate']:
                                          {code:
                                           {'sale': i['bid'], 'purchase': i['ask']}}})
                result.append(exchange_dict)
    return result



async def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    if days > 10:
        print('Too many days, max = 10')
    dates_raw = await gather_dates(days)
    dates_final = string_dates(dates_raw)
    urls = get_urls(dates_final)
    final = await exchange(urls)
    print(final)


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
            
    