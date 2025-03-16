import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_message_times: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Очистити застарілі записи з deque, які вийшли за межі window_size
        """
        if user_id not in self.user_message_times:
            return

        message_times = self.user_message_times[user_id]
        
        # Видаляємо всі записи, які вийшли за межі вікна
        while message_times and current_time - message_times[0] > self.window_size:
            message_times.popleft()

        # Якщо deque порожній після очищення, видаляємо запис користувача
        if not message_times:
            del self.user_message_times[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """
        Перевіряє, чи можна користувачу надіслати повідомлення
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        # Якщо користувача немає або він ще не надіслав жодного повідомлення, можна надсилати
        if user_id not in self.user_message_times:
            return True

        message_times = self.user_message_times[user_id]
        return len(message_times) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """
        Записує нове повідомлення, якщо це дозволено
        """
        current_time = time.time()

        if self.can_send_message(user_id):
            if user_id not in self.user_message_times:
                self.user_message_times[user_id] = deque()

            self.user_message_times[user_id].append(current_time)
            return True

        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Повертає час в секундах до моменту, коли користувач зможе надіслати нове повідомлення
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if self.can_send_message(user_id):
            return 0.0

        # Час, що залишився до дозволу на нове повідомлення
        message_times = self.user_message_times[user_id]
        oldest_message_time = message_times[0]
        time_passed = current_time - oldest_message_time
        wait_time = self.window_size - time_passed
        return max(wait_time, 0.0)

# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
