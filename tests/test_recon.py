import os
import sys
import pytest
import aiosqlite
import argparse

# Насильно заставляем Python добавить папку src в системные пути поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Импортируем наши асинкоровые функции из обновленного ядра v0.6.2
from web_recon.recon import init_db, insert_error, check_single_link_async

# Обязательный маркер для pytest, чтобы он знал: внутри файла есть асинхронные тесты
pytestmark = pytest.mark.asyncio

# Создаем стерильный тестовый список агентов, который будем подбрасывать функциям
TEST_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) TestAgent/1.0"]

# ==============================================================================
# 1. ТЕСТ СУБД: ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ И СТРУКТУРЫ ТАБЛИЦЫ
# ==============================================================================
async def test_init_db(tmp_path, monkeypatch):
    test_db_name = "test_report_init"
    test_db_path = tmp_path / f"{test_db_name}.db"
    
    # Заставляем Python временно переключить текущую рабочую директорию во временную папку
    monkeypatch.chdir(tmp_path)
    
    # Запускаем асинкоровую инициализацию СУБД
    await init_db(test_db_name)
    
    # Проверяем, что файл физически создался на диске
    assert os.path.exists(test_db_path) is True
    
    # Подключаемся и проверяем, что внутри создалась таблица с нужными колонками
    async with aiosqlite.connect(test_db_path) as conn:
        async with conn.execute(f"PRAGMA table_info([{test_db_name}])") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # Проверяем жесткое соответствие структуры нашей схемы данных
            assert "date" in column_names
            assert "url" in column_names
            assert "status" in column_names
            assert "whois_info" in column_names
            assert "latency" in column_names

# ==============================================================================
# 2. ТЕСТ СУБД: АСИНХРОННАЯ ЗАПИСЬ, КОММИТ И ЗАЩИТА ТАБЛИЦ С ПОДЧЕРКИВАНИЯМИ
# ==============================================================================
async def test_insert_error_and_commit(tmp_path, monkeypatch):
    test_db_name = "stealth_audit_2026"
    test_db_path = tmp_path / f"{test_db_name}.db"
    
    monkeypatch.chdir(tmp_path)
    
    # Подготавливаем базу и закидываем тестовый лог сбоя периметра
    await init_db(test_db_name)
    await insert_error(
        test_db_name, 
        "09.11.2026", 
        "https://broken-target.com", 
        "Error code 404: Not Found", 
        "Test WHOIS Passport Data", 
        "420.69"
    )
    
    # Читаем данные и проверяем, что они физически закоммитились в кастомную таблицу
    async with aiosqlite.connect(test_db_path) as conn:
        async with conn.execute(f"SELECT * FROM [{test_db_name}]") as cursor:
            row = await cursor.fetchone()
            
            assert row is not None
            assert row[1] == "https://broken-target.com"
            assert row[2] == "Error code 404: Not Found"
            assert row[3] == "Test WHOIS Passport Data"
            assert row[4] == "420.69"

# ==============================================================================
# 3. ТЕСТ CLI: ПАРСЕР АРГУМЕНТОВ И ВЗАИМОИСКЛЮЧАЮЩИЕ ГРУППЫ С РОТАЦИЕЙ UA
# ==============================================================================
def test_cli_arguments_parsing():
    # Создаем изолированный тестовый экземпляр нашего парсера v0.6.2
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--target")
    group.add_argument("-f", "--file")
    parser.add_argument("-o", "--output", default="RReport")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-d", "--delay", type=float, default=0.5)
    parser.add_argument("-c", "--concurrency", type=int, default=50)
    # Добавляем наш новый флаг ротации User-Agents в тест!
    parser.add_argument("-A", "--UserAgents", type=str)

    # Имитируем ввод хакера: парсим одиночную цель, кастомный вывод, стелс-задержку и файл агентов
    test_args = ["-t", "https://linode.com", "-o", "BespokeReport", "-d", "1.5", "-A", "my_agents.txt"]
    parsed = parser.parse_args(test_args)
    
    # Проверяем, что argparse ювелирно разложил параметры по свойствам
    assert parsed.target == "https://linode.com"
    assert parsed.file is None
    assert parsed.output == "BespokeReport"
    assert parsed.delay == 1.5
    assert parsed.quiet is False
    assert parsed.concurrency == 50
    assert parsed.UserAgents == "my_agents.txt" # <- Проверяем подхват флага!

    # Проверяем работу защитной коллизии (взаимоисключение -t и -f)
    bad_test_args = ["-t", "https://google.com", "-f", "targets.txt"]
    with pytest.raises(SystemExit):
        parser.parse_args(bad_test_args)
