import os
import sys
import pytest
import aiosqlite
import argparse
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# ВАЖНО: подгони имя модуля под реальный файл v0.7.0
# если файл называется recon0.7.0.py — импорт невозможен (точка в имени),
# переименуй в recon.py или recon_v07.py
from web_recon.recon import (
    init_db,
    insert_error,
    check_single_link_async,
    check_for_updates,
    export_to_csv,
    check_your_domain_info,
)

pytestmark = pytest.mark.asyncio

TEST_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) TestAgent/1.0"]


# ==============================================================================
# 1. СУБД: ИНИЦИАЛИЗАЦИЯ
# ==============================================================================
async def test_init_db(tmp_path, monkeypatch):
    test_db_name = "test_report_init"
    test_db_path = tmp_path / f"{test_db_name}.db"
    monkeypatch.chdir(tmp_path)

    await init_db(test_db_name)

    assert os.path.exists(test_db_path) is True

    async with aiosqlite.connect(test_db_path) as conn:
        async with conn.execute(f"PRAGMA table_info([{test_db_name}])") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            assert {"date", "url", "status", "whois_info", "latency"} <= set(column_names)


# ==============================================================================
# 2. СУБД: ЗАПИСЬ И КОММИТ
# ==============================================================================
async def test_insert_error_and_commit(tmp_path, monkeypatch):
    test_db_name = "stealth_audit_2026"
    test_db_path = tmp_path / f"{test_db_name}.db"
    monkeypatch.chdir(tmp_path)

    await init_db(test_db_name)
    await insert_error(
        test_db_name,
        "09.11.2026",
        "https://broken-target.com",
        "Error code 404: Not Found",
        "Test WHOIS Passport Data",
        "420.69",
    )

    async with aiosqlite.connect(test_db_path) as conn:
        async with conn.execute(f"SELECT * FROM [{test_db_name}]") as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row[1] == "https://broken-target.com"
            assert row[2] == "Error code 404: Not Found"
            assert row[3] == "Test WHOIS Passport Data"
            assert row[4] == "420.69"


# ==============================================================================
# 3. CLI: ПАРСЕР АРГУМЕНТОВ (включая новый -cT/--csv)
# ==============================================================================
def test_cli_arguments_parsing():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--target")
    group.add_argument("-f", "--file")
    parser.add_argument("-o", "--output", default="RReport")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-d", "--delay", type=float, default=0.5)
    parser.add_argument("-c", "--concurrency", type=int, default=50)
    parser.add_argument("-A", "--UserAgents", type=str)
    parser.add_argument("-cT", "--csv", action="store_true")  # НОВОЕ в v0.7.0

    test_args = ["-t", "https://linode.com", "-o", "BespokeReport",
                 "-d", "1.5", "-A", "my_agents.txt", "-cT"]
    parsed = parser.parse_args(test_args)

    assert parsed.target == "https://linode.com"
    assert parsed.file is None
    assert parsed.output == "BespokeReport"
    assert parsed.delay == 1.5
    assert parsed.quiet is False
    assert parsed.concurrency == 50
    assert parsed.UserAgents == "my_agents.txt"
    assert parsed.csv is True  # <- проверяем новый флаг

    bad_test_args = ["-t", "https://google.com", "-f", "targets.txt"]
    with pytest.raises(SystemExit):
        parser.parse_args(bad_test_args)


# ==============================================================================
# 4. НОВОЕ: CSV-ЭКСПОРТ (v0.7.0)
# ==============================================================================
def test_export_to_csv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    results = [
        {"url": "https://a.com", "status": "Working",
         "passport": "Not checked for working sites", "latency": 123.4},
        {"url": "https://b.com", "status": "Error code 500: Server Error",
         "passport": "WHOIS\nmultiline", "latency": 999.9},
    ]
    export_to_csv("out", results)

    out_file = tmp_path / "out.csv"
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8-sig")
    # заголовок и обе строки на месте
    assert "Date;URL;Status;WHOIS;Latency" in content
    assert "https://a.com" in content
    assert "https://b.com" in content
    # переводы строк в WHOIS схлопнуты в пробел
    assert "WHOIS multiline" in content


# ==============================================================================
# 5. НОВОЕ: check_for_updates (сеть замокана)
# ==============================================================================
def test_check_for_updates_success():
    with patch("web_recon.recon.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"tag_name": "v0.7.0"}
        result = check_for_updates()
        assert result == "v0.7.0"


def test_check_for_updates_fallback_on_error():
    with patch("web_recon.recon.requests.get", side_effect=Exception("no net")):
        result = check_for_updates()
        assert result.startswith("v")  # возвращает текущую версию, не падает


# ==============================================================================
# 6. check_single_link_async: рабочий сайт НЕ дергает WHOIS
# ==============================================================================
async def test_check_single_link_working_no_whois():
    fake_response = MagicMock()
    fake_response.status = 200
    fake_response.reason = "OK"
    fake_response.__aenter__ = AsyncMock(return_value=fake_response)
    fake_response.__aexit__ = AsyncMock(return_value=False)

    fake_session = MagicMock()
    fake_session.get = MagicMock(return_value=fake_response)

    import asyncio as _asyncio
    sem = _asyncio.Semaphore(1)

    with patch("web_recon.recon.check_your_domain_info") as mock_whois:
        result = await check_single_link_async(
            fake_session, "https://ok.com", sem, 0, TEST_AGENTS[0]
        )
        mock_whois.assert_not_called()  # рабочий сайт — WHOIS не нужен
        assert result["status"] == "Working"
        assert result["passport"] == "Not checked for working sites"
        assert isinstance(result["latency"], float)
