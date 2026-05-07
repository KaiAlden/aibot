from scripts.seed_symptoms import seed_symptoms


def test_seed_symptoms_dry_run_builds_nine_rows() -> None:
    rows = seed_symptoms(dry_run=True)

    assert len(rows) == 9
    assert rows[0]["constitution_name"] == "平和质"
    assert len(rows[0]["vector"]) == 1024
