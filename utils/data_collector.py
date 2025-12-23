from utils.API import API_KEY
import requests
import time
import json

BASE_URL = 'https://api.etherscan.io/v2/api'


def create_micro_dataset():
    # Известные активные источники
    source_contracts = [
        '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
        '0xdac17f958d2ee523a2206206994597c13d831ec7',
        '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    ]

    all_addresses = set()

    for contract in source_contracts:
        print(f"Получаю транзакции для контракта {contract[:10]}...")

        # Последние транзакции
        params = {
            'apikey': API_KEY,
            'module': 'account',
            'action': 'txlist',
            'address': contract,
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': 50,  # 50 последних транзакций
            'sort': 'desc',
            'chainid': 1
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()

            if data.get('status') == '1':
                for tx in data['result']:
                    # Собираем всех участников
                    all_addresses.add(tx['from'].lower())
                    if tx['to']:
                        all_addresses.add(tx['to'].lower())

                print(f"Найдено {len(data['result'])} транзакций, уникальных адресов: {len(all_addresses)}")
            else:
                print(f"Нет транзакций или ошибка")

        except Exception as e:
            print(f"   Ошибка: {e}")

        time.sleep(0.25)

    # 2. Преобразуем в список и сохраняем
    address_list = list(all_addresses)

    with open('micro_real_addresses.json', 'w') as f:
        json.dump(address_list, f, indent=2)

    print(f"\nСОЗДАН МИКРО-ДАТАСЕТ: {len(address_list)} реальных адресов")
    print("Файл: 'micro_real_addresses.json'")

    # Примеры
    print("\nПримеры адресов в датасете:")
    for i, addr in enumerate(address_list[:5]):
        print(f"  {i + 1}. {addr}")

    return address_list


# Запуск создания датасета
if __name__ == "__main__":
    real_addresses = create_micro_dataset()


