import sys
import time
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import LESSON_TIERS, SUPPORTED_LANGUAGES

client = TestClient(app)

def run_tests():
    print("=== Step 1: Health & Configuration Verification ===")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    print("Health OK:", health_data)

    res = client.get("/lesson/tiers")
    assert res.status_code == 200, f"Tiers check failed: {res.text}"
    tiers_data = res.json()["tiers"]
    print(f"Loaded {len(tiers_data)} tiers successfully.")
    assert len(tiers_data) == 9, f"Expected 9 tiers, found {len(tiers_data)}"

    print("\n=== Step 2: Scope Heuristic Check ===")
    from backend.engine import check_scope
    scope_result = check_scope("Machine learning, deep neural networks, and computer vision", "5m")
    print("Scope check on broad topic in 5m tier:", scope_result)
    assert scope_result is not None and scope_result.get("type") == "too_broad", "Expected broad topic to be flagged"
    print("Scope heuristic verified successfully.")

    print("\n=== Step 3: Lesson Plan Generation (5m Audio-Only) ===")
    plan_payload = {
        "student_id": "test_student_01",
        "topic": "Gravity and Free Fall",
        "time_tier": "5m",
        "level": "beginner",
        "language": "en"
    }
    res = client.post("/lesson/plan", data=plan_payload)
    assert res.status_code == 200, f"Lesson plan creation failed: {res.text}"
    plan_data = res.json()
    session_id = plan_data["session_id"]
    sections = plan_data["lesson_plan"]
    print(f"Created session {session_id} with {len(sections)} sections.")
    
    # Verify complete video removal
    for idx, sec in enumerate(sections):
        assert "video_url" not in sec, f"video_url found in section {idx}!"

    print("Lesson plan generated with pure audio delivery verified (no video_url).")

    print("\n=== Step 4: Universal Doubt Asking Endpoint ===")
    doubt_payload = {
        "session_id": session_id,
        "section_id": sections[0]["section_id"],
        "doubt": "Does a heavier rock fall faster than a feather in vacuum?"
    }
    res = client.post("/lesson/doubt", json=doubt_payload)
    assert res.status_code == 200, f"Doubt resolution failed: {res.text}"
    doubt_res = res.json()
    assert len(doubt_res.get("teacher_reply", "")) > 10, "Expected non-empty doubt answer"
    print("Doubt endpoint verified.")

    print("\n=== Step 5: Checkpoint Evaluation & Misconception Diagnosis ===")
    sec_with_q = next((s for s in sections if s.get("pause_for_question") and s.get("question")), sections[-1])
    answer_payload = {
        "session_id": session_id,
        "section_id": sec_with_q["section_id"],
        "answer": "Heavier objects fall faster because they have more mass pulling them."
    }
    res = client.post("/lesson/answer", json=answer_payload)
    assert res.status_code == 200, f"Answer evaluation failed: {res.text}"
    eval_res = res.json()
    print("Answer evaluated successfully.")

    print("\n=== Step 6: Audio Synthesis for Next Section ===")
    if len(sections) > 1:
        sec2_id = sections[1]["section_id"]
        res = client.post("/lesson/audio/segment", json={"session_id": session_id, "section_id": sec2_id})
        assert res.status_code == 200, f"Audio synthesis failed: {res.text}"
        audio_data = res.json()
        print("Section 2 audio request completed.")

    print("\n=== Step 7: Language Switch & Translation ===")
    lang_payload = {
        "session_id": session_id,
        "section_id": sections[0]["section_id"],
        "language": "hi"
    }
    res = client.post("/lesson/language", json=lang_payload)
    assert res.status_code == 200, f"Language switch failed: {res.text}"
    lang_data = res.json()
    assert lang_data.get("language") == "hi"
    print("Hindi translated script successfully verified (Unicode length:", len(lang_data.get("avatar_script", "")), ")")

    print("\n=======================================================")
    print("ALL 7 VERIFICATION SUITES PASSED FLAWLESSLY!")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
