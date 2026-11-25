"""
Юніт-тести для Лабораторної роботи № 7 (Варіант 11: аналіз журналу подій log.txt).
"""
import os
import tempfile
import unittest

from src.lab7 import (
     DEFAULT_LOG_PATH,
    count_events_in_period,
    find_most_active_ip,
    read_log_file,
    save_events_by_ip,
)


class TestLab7Variant11(unittest.TestCase):
    """Перевірка функцій читання, фільтрації та обробки помилок для log.txt."""

    def test_read_default_log_file(self):
        """Перевірка успішного читання штатного файлу src/log.txt."""
        events = read_log_file(DEFAULT_LOG_PATH)
        self.assertGreaterEqual(len(events), 10)
        self.assertIn("time", events[0])
        self.assertIn("event", events[0])
        self.assertIn("ip", events[0])

    def test_count_events_in_period(self):
        """Перевірка підрахунку кількості подій у заданому часовому діапазоні."""
        events = read_log_file(DEFAULT_LOG_PATH)
        period_events = count_events_in_period(events, "09:00:00", "12:00:00")
        self.assertEqual(len(period_events), 7)

    def test_save_events_by_ip(self):
        """Перевірка запису відфільтрованих за IP подій у файл."""
        events = read_log_file(DEFAULT_LOG_PATH)
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = os.path.join(tmp_dir, "events_by_ip.txt")
            count = save_events_by_ip(events, "10.0.0.44", out_file)
            self.assertEqual(count, 3)
            with open(out_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            self.assertEqual(len(lines), 3)

    def test_find_most_active_ip(self):
        """Перевірка визначення IP-адреси з найбільшою кількістю подій."""
        top_ip, top_count = find_most_active_ip(DEFAULT_LOG_PATH)
        self.assertEqual(top_ip, "192.168.1.10")
        self.assertEqual(top_count, 5)

    def test_error_handling_missing_and_invalid_files(self):
        """Перевірка генерації FileNotFoundError та ValueError."""
        with self.assertRaises(FileNotFoundError):
            read_log_file("non_existent_log_12345.txt")

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as bad_file:
            bad_file.write("некоректний_час,LOGIN,192.168.1.1\n")
            bad_path = bad_file.name
        try:
            with self.assertRaises(ValueError):
                read_log_file(bad_path)
        finally:
            os.remove(bad_path)


if __name__ == "__main__":
    unittest.main()
