"""Скачивание датасета PaySim с Kaggle в папку data/.

Запуск:  python data/download.py
"""
import shutil
from pathlib import Path

import kagglehub

# Папка, где лежит ЭТОТ скрипт (…/Transaction-Monitoring/data)
DATA_DIR = Path(__file__).resolve().parent


def main() -> None:
    # 1. Скачиваем датасет в локальный кеш Kaggle, получаем путь к папке
    cache_path = kagglehub.dataset_download("ealaxi/paysim1")
    print(f"Скачано в кеш Kaggle: {cache_path}")

    # 2. Находим CSV внутри скачанной папки
    csv_files = list(Path(cache_path).glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"CSV не найден в {cache_path}")
    src = csv_files[0]

    # 3. Копируем его в data/ под простым именем
    dst = DATA_DIR / "paysim.csv"
    shutil.copy(src, dst)
    print(f"Готово. Датасет здесь: {dst}")


if __name__ == "__main__":
    main()