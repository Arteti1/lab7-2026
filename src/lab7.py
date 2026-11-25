"""
Лабораторна робота № 7. Читання та запис даних у файли.
Варіант 11: Обробка журналу подій log.txt у форматі «Час,Подія,IP-адреса».
Студент: Фесюк Максим Ігорович (КН-25-2)
"""
from collections import Counter
from datetime import datetime, time
import os
from typing import Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOG_PATH = os.path.join(BASE_DIR, "log.txt")
DEFAULT_OUTPUT_PATH = os.path.join(BASE_DIR, "events_by_ip.txt")
TIME_FORMAT = "%H:%M:%S"


def resolve_path(filename: str) -> str:
    """Повертає коректний шлях до файлу (відносно поточної папки або директорії src)."""
    filename = filename.strip()
    if os.path.exists(filename):
        return filename
    candidate = os.path.join(BASE_DIR, filename)
    if os.path.exists(candidate):
        return candidate
    return filename


def parse_time(time_str: str) -> time:
    """Перетворює рядок формату ГГ:ХХ:СС у об'єкт datetime.time."""
    return datetime.strptime(time_str.strip(), TIME_FORMAT).time()


def read_log_file(filepath: str) -> List[Dict[str, str]]:
    """
    Читає файл журналу у форматі «Час,Подія,IP-адреса».
    Генерує FileNotFoundError, ValueError або IOError у разі помилок.
    """
    events: List[Dict[str, str]] = []
    with open(filepath, "r", encoding="utf-8") as file:
        for line_num, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                continue
            parts = [part.strip() for part in line.split(",")]
            if len(parts) != 3 or not all(parts):
                raise ValueError(
                    f"Некоректний формат у рядку {line_num}: '{line}'. "
                    "Очікується «Час,Подія,IP-адреса»."
                )
            event_time_str, event_type, ip_address = parts
            # Перевірка валідності часу (викличе ValueError, якщо час некоректний)
            parse_time(event_time_str)
            events.append(
                {
                    "time": event_time_str,
                    "event": event_type,
                    "ip": ip_address,
                    "raw": f"{event_time_str},{event_type},{ip_address}",
                }
            )
    return events


def count_events_in_period(
    events: List[Dict[str, str]], start_str: str, end_str: str
) -> List[Dict[str, str]]:
    """Повертає список подій, які відбулися у проміжку [start_str, end_str]."""
    start_t = parse_time(start_str)
    end_t = parse_time(end_str)
    if start_t > end_t:
        raise ValueError("Початковий час не може бути більшим за кінцевий час.")

    return [
        item
        for item in events
        if start_t <= parse_time(item["time"]) <= end_t
    ]


def save_events_by_ip(
    events: List[Dict[str, str]], target_ip: str, output_path: str = DEFAULT_OUTPUT_PATH
) -> int:
    """
    Записує всі події з вказаної IP-адреси у файл events_by_ip.txt.
    Повертає кількість записаних подій.
    """
    target_ip = target_ip.strip()
    if not target_ip:
        raise ValueError("IP-адреса не може бути порожньою.")

    matched = [item["raw"] for item in events if item["ip"] == target_ip]
    with open(output_path, "w", encoding="utf-8") as out_file:
        if matched:
            out_file.write("\n".join(matched) + "\n")
    return len(matched)


def find_most_active_ip(filepath: str) -> Tuple[str, int]:
    """
    Читає вказаний файл журналу та знаходить IP-адресу з найбільшою кількістю подій.
    Повертає кортеж (ip_адреса, кількість_подій).
    """
    events = read_log_file(filepath)
    if not events:
        raise ValueError("Файл журналу порожній — неможливо визначити найактивніший IP.")
    counts = Counter(item["ip"] for item in events)
    return counts.most_common(1)[0]


def main() -> None:
    """Головна інтерактивна функція програми для Варіанту 11."""
    print("=== Лабораторна робота № 7 (Варіант 11: Аналіз журналу подій) ===\n")

    # 1–2. Читання файлу log.txt та підрахунок кількості подій за період часу
    try:
        events = read_log_file(DEFAULT_LOG_PATH)
        print(f"Успішно прочитано {len(events)} записів із файлу 'log.txt':")
        for item in events:
            print(f"  [{item['time']}] {item['event']:<16} | IP: {item['ip']}")
    except FileNotFoundError:
        print(f"Помилка: Файл '{DEFAULT_LOG_PATH}' не знайдено!")
        return
    except ValueError as err:
        print(f"Помилка формату даних у файлі 'log.txt': {err}")
        return
    except IOError as err:
        print(f"Помилка читання файлу 'log.txt': {err}")
        return

    print("\n--- Підрахунок подій за період часу ---")
    start_input = input("Введіть початковий час ГГ:ХХ:СС (Enter = 09:00:00): ").strip() or "09:00:00"
    end_input = input("Введіть кінцевий час ГГ:ХХ:СС (Enter = 12:00:00): ").strip() or "12:00:00"

    try:
        period_events = count_events_in_period(events, start_input, end_input)
        print(
            f"Кількість подій у період з {start_input} до {end_input}: "
            f"{len(period_events)}"
        )
        for item in period_events:
            print(f"  -> {item['raw']}")
    except ValueError as err:
        print(f"Помилка введення часу: {err}")

    # 3. Запит IP-адреси та запис подій у events_by_ip.txt
    print("\n--- Фільтрація подій за IP-адресою ---")
    ip_input = input(
        "Введіть IP-адресу для збереження подій (наприклад, 192.168.1.10): "
    ).strip()
    try:
        written_count = save_events_by_ip(events, ip_input, DEFAULT_OUTPUT_PATH)
        if written_count > 0:
            print(
                f"Знайдено {written_count} подій для IP '{ip_input}'. "
                f"Дані записано у '{DEFAULT_OUTPUT_PATH}'."
            )
        else:
            print(
                f"Подій для IP '{ip_input}' не знайдено "
                f"(створено порожній файл '{DEFAULT_OUTPUT_PATH}')."
            )
    except ValueError as err:
        print(f"Помилка значення IP: {err}")
    except IOError as err:
        print(f"Помилка запису у файл 'events_by_ip.txt': {err}")

    # 4. Запит імені файлу та пошук IP з найбільшою кількістю подій
    print("\n--- Пошук найактивнішої IP-адреси у файлі ---")
    user_filename = (
        input("Введіть ім'я файлу для аналізу (Enter = log.txt): ").strip() or "log.txt"
    )
    resolved = resolve_path(user_filename)
    try:
        top_ip, top_count = find_most_active_ip(resolved)
        print(
            f"IP-адреса з найбільшою кількістю подій у файлі '{user_filename}': "
            f"{top_ip} ({top_count} подій)"
        )
    except FileNotFoundError:
        print(f"Помилка: Файл '{user_filename}' не знайдено!")
    except ValueError as err:
        print(f"Помилка обробки даних у файлі '{user_filename}': {err}")
    except IOError as err:
        print(f"Помилка читання файлу '{user_filename}': {err}")


if __name__ == "__main__":
    main()
