from lifeos.storage import connect, list_notes, save_note, delete_note


def test_notes_crud(tmp_path):
    db = connect(tmp_path / "test.db")
    note_id = save_note(db, "  Physics  ", "Motion and forces")
    notes = list_notes(db)
    assert len(notes) == 1
    assert notes[0]["title"] == "Physics"
    save_note(db, "Physics", "Updated content", note_id)
    assert list_notes(db)[0]["body"] == "Updated content"
    delete_note(db, note_id)
    assert list_notes(db) == []
    db.close()
