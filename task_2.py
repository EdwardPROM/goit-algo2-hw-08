import time
from typing import Dict
import random

class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval  # Мінімальний інтервал між повідомленнями
        self.user_last_message_time: Dict[str, float] = {}  # Зберігає час останнього повідомлення користувача

    def can_send_message(self, user_id: str) -> bool:
        """
        Перевіряє, чи користувач може надіслати повідомлення
        """
        current_time = time.time()

        # Якщо користувача ще не було, можна відправити
        if user_id not in self.user_last_message_time:
            return True
        
        last_time = self.user_last_message_time[user_id]

        # Чи пройшло достатньо часу з моменту останнього повідомлення
        return (current_time - last_time) >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        """
        Записує новий час відправлення повідомлення, якщо дозволено
        """
        if self.can_send_message(user_id):
            self.user_last_message_time[user_id] = time.time()
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Повертає час в секундах, скільки залишилось чекати користувачу
        """
        current_time = time.time()

        if user_id not in self.user_last_message_time:
            return 0.0
        
        last_time = self.user_last_message_time[user_id]
        elapsed_time = current_time - last_time
        wait_time = self.min_interval - elapsed_time

        return max(wait_time, 0.0)

# Тестова функція
def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\n=== Симуляція потоку повідомлень (Throttling) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Випадкова затримка між повідомленнями
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 10 секунд...")
    time.sleep(10)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_throttling_limiter()
