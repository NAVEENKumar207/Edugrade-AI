"""
Transcript Cryptographic Issuance and Public Verification Service for EduGrade AI.
Creates tamper-proof snapshots, computes SHA-256 hashes, generates HMAC signatures,
and handles public verification requests.
"""

import hmac
import hashlib
import json
from django.conf import settings
from django.utils import timezone
from core.models import UserProfile, SemesterRecord, TranscriptIssue

def mask_name(full_name: str) -> str:
    """Masks name: first letter + stars (e.g., 'Kavitha' -> 'K******')."""
    cleaned = (full_name or "").strip()
    if not cleaned:
        return "S****"
    return cleaned[0].upper() + ("*" * max(3, len(cleaned) - 1))

def mask_roll(roll_number: str) -> str:
    """Masks roll number: keeps only the last 3 characters visible."""
    cleaned = (roll_number or "").strip()
    if not cleaned:
        return "***"
    if len(cleaned) <= 3:
        return cleaned
    return ("*" * (len(cleaned) - 3)) + cleaned[-3:]

def get_transcript_signing_key() -> str:
    """Retrieves signing key falling back to SECRET_KEY."""
    return getattr(settings, 'TRANSCRIPT_SIGNING_KEY', None) or settings.SECRET_KEY

def compute_snapshot_hash(snapshot_dict: dict) -> str:
    """Computes deterministic SHA-256 hash of sorted snapshot JSON."""
    raw_json = json.dumps(snapshot_dict, sort_keys=True)
    return hashlib.sha256(raw_json.encode('utf-8')).hexdigest()

def compute_signature(snapshot_hash: str) -> str:
    """Generates HMAC-SHA256 signature using the institutional signing key."""
    key = get_transcript_signing_key().encode('utf-8')
    return hmac.new(key, snapshot_hash.encode('utf-8'), hashlib.sha256).hexdigest()

def issue_or_reuse_transcript(student_profile) -> TranscriptIssue:
    """
    Issues a new cryptographically signed TranscriptIssue or reuses an existing
    non-revoked record if the academic records are identical.
    """
    user = student_profile.user
    full_name = f"{user.first_name} {user.last_name}".strip() or user.username
    sem_count = SemesterRecord.objects.filter(student=student_profile).count()

    masked_name_str = mask_name(full_name)
    masked_roll_str = mask_roll(student_profile.roll_number)

    # Check for existing non-revoked issue for this student with identical academic state
    existing_issue = TranscriptIssue.objects.filter(
        student=student_profile,
        is_revoked=False
    ).order_by('-issued_at').first()

    if existing_issue and isinstance(existing_issue.snapshot, dict):
        snap = existing_issue.snapshot
        if (
            snap.get("student_id") == student_profile.id and
            snap.get("masked_name") == masked_name_str and
            snap.get("masked_roll") == masked_roll_str and
            snap.get("department") == (student_profile.department or "General Engineering") and
            float(snap.get("cgpa", 0.0)) == float(student_profile.current_cgpa or 0.0) and
            int(snap.get("credits_earned", 0)) == int(student_profile.credits_earned or 0) and
            int(snap.get("backlogs", 0)) == int(student_profile.backlogs_count or 0) and
            int(snap.get("semester_count", 0)) == int(sem_count)
        ):
            return existing_issue

    # Generate new snapshot
    issue_date = timezone.now().strftime("%Y-%m-%d")
    snapshot = {
        "student_id": student_profile.id,
        "masked_name": masked_name_str,
        "masked_roll": masked_roll_str,
        "department": student_profile.department or "General Engineering",
        "cgpa": float(student_profile.current_cgpa or 0.0),
        "credits_earned": int(student_profile.credits_earned or 0),
        "backlogs": int(student_profile.backlogs_count or 0),
        "semester_count": int(sem_count),
        "issue_date": issue_date,
    }

    snap_hash = compute_snapshot_hash(snapshot)
    sig = compute_signature(snap_hash)

    new_issue = TranscriptIssue.objects.create(
        student=student_profile,
        snapshot=snapshot,
        snapshot_hash=snap_hash,
        signature=sig,
        is_revoked=False
    )
    return new_issue

def verify_transcript_token(token: str) -> dict:
    """
    Public cryptographic verification of a transcript issue token.
    Validates existence, revocation status, data integrity hash, and HMAC signature.
    Never exposes internal database primary keys, emails, or full roll numbers.
    """
    clean_token = str(token).strip()
    issue = TranscriptIssue.objects.filter(token=clean_token).first()

    if not issue:
        return {
            "is_valid": False,
            "status": "NOT VALID",
            "reason": "Unknown or unissued transcript token."
        }

    if issue.is_revoked:
        return {
            "is_valid": False,
            "status": "NOT VALID",
            "reason": "This transcript has been officially revoked by institutional authority."
        }

    # Verify SHA-256 integrity hash
    expected_hash = compute_snapshot_hash(issue.snapshot)
    if not hmac.compare_digest(expected_hash, issue.snapshot_hash):
        return {
            "is_valid": False,
            "status": "NOT VALID",
            "reason": "Transcript snapshot data integrity check failed (altered record)."
        }

    # Verify HMAC-SHA256 cryptographic signature
    expected_sig = compute_signature(issue.snapshot_hash)
    if not hmac.compare_digest(expected_sig, issue.signature):
        return {
            "is_valid": False,
            "status": "NOT VALID",
            "reason": "Cryptographic signature verification failed (tampered record)."
        }

    snap = issue.snapshot or {}
    return {
        "is_valid": True,
        "status": "VALID",
        "issue_date": snap.get("issue_date") or issue.issued_at.strftime("%Y-%m-%d"),
        "masked_name": snap.get("masked_name", "S****"),
        "masked_roll": snap.get("masked_roll", "***"),
        "department": snap.get("department", "Engineering"),
        "cgpa": float(snap.get("cgpa", 0.0)),
        "credits_earned": int(snap.get("credits_earned", 0)),
        "backlogs": int(snap.get("backlogs", 0)),
        "semester_count": int(snap.get("semester_count", 0)),
        "token": issue.token,
        "note": "This is a snapshot taken on the issue date; current records may differ."
    }
