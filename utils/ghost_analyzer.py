import datetime
import json
import requests
import time
from utils.data_collector import BASE_URL
from utils.API import API_KEY

with open('micro_real_addresses.json', 'r') as f:
    addresses_to_check = json.load(f)

def get_address_transactions(address):
    params = {
        'apikey': API_KEY,
        'module': 'account',
        'action': 'balance',
        'address': address,
        'chainid': 1
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data

def get_last_transaction(address):
    params = {
        'apikey': API_KEY,
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'page': 1,
        'offset': 1,
        'sort': 'desc',
        'chainid': 1
    }

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data.get('status') == '1' and data['result']:
            timestamp = int(data['result'][0]['timeStamp'])
            return datetime.datetime.fromtimestamp(timestamp)
        else:
            return None

    except Exception as e:
        print(f"Ошибка при запросе транзакций для {address}: {e}")
        return None



def analyze_address():
    ghost_addresses = set()

    total = len(addresses_to_check)
    active_count = 0
    empty_count = 0
    no_tx_count = 0
    start_time = time.time()

    for i, address in enumerate(addresses_to_check, 1):
        print(f"[{i:3}/{total:3}] Анализирую {address[:12]}...", end=' ')

        # Получаем баланс
        balance_data = get_address_transactions(address)

        # Проверяем запрос баланса
        if balance_data.get('status') != '1':
            print(f"Ошибка баланса.")
            continue

        # Извлекаем баланс и конвертируем в ETH
        balance_wei = int(balance_data['result'])
        balance_eth = balance_wei / 10 ** 18

        # Получаем дату последней транзакции
        last_tx_date = get_last_transaction(address)

        # Определяем, является ли адрес "призраком"
        is_ghost = False

        if balance_eth > 0.01 and last_tx_date is not None:
            # Вычисляем, сколько лет прошло
            time_passed = datetime.datetime.now() - last_tx_date
            years_passed = time_passed.days / 365.25

            if years_passed >= 3:
                is_ghost = True

        if is_ghost:
            ghost_addresses.add(address)
            print(f"НАЙДЕН! ({balance_eth:.4f} ETH, спит {years_passed:.1f} лет)")
        else:
            if balance_eth <= 0.01:
                empty_count += 1
                print(f"Пуст/мал ({balance_eth:.4f} ETH)")
            elif last_tx_date is None:
                no_tx_count += 1
                print(f"Нет транзакций")
            else:
                active_count += 1
                years_passed = (datetime.datetime.now() - last_tx_date).days / 365.25
                print(f"Активен ({years_passed:.1f} лет назад)")

        time.sleep(0.25)

    time_elapsed = time.time() - start_time

    return {
        'ghost_addresses': ghost_addresses,
        'total': total,
        'active_count': active_count,
        'empty_count': empty_count,
        'no_tx_count': no_tx_count,
        'time_elapsed': time_elapsed
    }


if __name__ == "__main__":
    print("Запуск анализа датасета...")
    results = analyze_address()

    print(f"\n{'=' * 50}")
    print(f"""
        ИТОГОВАЯ СТАТИСТИКА
        {'=' * 30}
        Всего проверено адресов: {results['total']}
        Найдено призраков: {len(results['ghost_addresses'])}
        Распределение:
          • Активны (<3 лет): {results['active_count']}
          • Пустые/мал.баланс: {results['empty_count']}
          • Без транзакций: {results['no_tx_count']}
        Время выполнения: {results['time_elapsed']:.1f} сек
        """)

    # Вывод списка найденных призраков
    if results['ghost_addresses']:
        print("\nСписок найденных адресов-призраков:")
        for addr in results['ghost_addresses']:
            print(f"  • {addr}")

