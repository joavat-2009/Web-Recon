import os
import sys
import pytest
import aiosqlite
import argparse
from src.web_recon.recon import init_db, insert_error, check_single_link_async


from recon import init_db, insert_error, check_single_link_async

pytestmark = pytest.mark.asyncio


async def test_init_db(tmp_path, monkeypatch): # <- Добавь фикстуру monkeypatch
    test_db_name = "test_report_init"
    test_db_path = tmp_path / f"{test_db_name}.db"
    
    monkeypatch.chdir(tmp_path)
  
    await init_db(test_db_name)
    
    assert os.path.exists(test_db_path) is True
    
    async with aiosqlite.connect(test_db_path) as conn:
        async with conn.execute(f"PRAGMA table_info([{test_db_name}])") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns] 
            
            assert "date" in column_names
            assert "url" in column_names
            assert "status" in column_names
            assert "whois_info" in column_names
            assert "latency" in column_names



async def test_insert_error_and_commit(tmp_path, monkeypatch): 
    test_db_name = "stealth_audit_2026"
    test_db_path = tmp_path / f"{test_db_name}.db"
    
    monkeypatch.chdir(tmp_path)
    
    await init_db(test_db_name)
    await insert_error(
        test_db_name,
        "08.11.2026", 
        "https://broken-target.com", 
        "Error code 404: Not Found", 
        "Test WHOIS Passport Data", 
        "420.69"
    )
    
    async with aiosqlite.connect(test_db_path) as conn:
        async with conn.execute(f"SELECT * FROM [{test_db_name}]") as cursor:
            row = await cursor.fetchone()
            
            assert row is not None
            assert row[1] == "https://broken-target.com"
            assert row[2] == "Error code 404: Not Found"
            assert row[3] == "Test WHOIS Passport Data"
            assert row[4] == "420.69"


def test_cli_arguments_parsing():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--target")
    group.add_argument("-f", "--file")
    parser.add_argument("-o", "--output", default="RReport")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-d", "--delay", type=float, default=0.5)
    parser.add_argument("-c", "--concurrency", type=int, default=50)

    test_args = ["-t", "https://linode.com", "-o", "BespokeReport", "-d", "1.5"]
    parsed = parser.parse_args(test_args)
    
    assert parsed.target == "https://linode.com"
    assert parsed.file is None
    assert parsed.output == "BespokeReport"
    assert parsed.delay == 1.5
    assert parsed.quiet is False
    assert parsed.concurrency == 50

    bad_test_args = ["-t", "https://google.com", "-f", "targets.txt"]
    with pytest.raises(SystemExit):
        parser.parse_args(bad_test_args)
