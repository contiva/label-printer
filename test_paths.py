import importlib


def test_generator_uses_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("LABEL_PRINTER_DATA_DIR", str(tmp_path))
    (tmp_path / "serial_number.txt").write_text("42000")

    import generator
    importlib.reload(generator)
    generator.generate_image_with_optimal_size()

    assert (tmp_path / "serial_qr.png").exists()
    assert (tmp_path / "serial_number.txt").read_text().strip() == "42001"


def test_generator_with_date_uses_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("LABEL_PRINTER_DATA_DIR", str(tmp_path))
    (tmp_path / "serial_number.txt").write_text("42000")

    import generator_with_date
    importlib.reload(generator_with_date)
    generator_with_date.generate_image_with_optimal_size()

    assert (tmp_path / "serial_qr.png").exists()
    assert (tmp_path / "serial_number.txt").read_text().strip() == "42001"


def test_generator_asset_uses_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("LABEL_PRINTER_DATA_DIR", str(tmp_path))

    import generator_asset
    importlib.reload(generator_asset)
    generator_asset.generate_image_with_optimal_size(12345)

    assert (tmp_path / "serial_qr.png").exists()
