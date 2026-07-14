-- Seed: selections (Brazil, Argentina, France) + one user per role per selection.
-- Password for every seeded user: Password123!
-- Safe to re-run: skips rows that already exist (unique code / email).

INSERT INTO selection (id, name, code, created_at)
VALUES
    (gen_random_uuid(), 'Brazil', 'BRA', now()),
    (gen_random_uuid(), 'Argentina', 'ARG', now()),
    (gen_random_uuid(), 'France', 'FRA', now())
ON CONFLICT (code) DO NOTHING;

-- NOTE: the `userrole` enum type in this DB has a mislabeled value for
-- medical staff (stored as 'gitr' instead of 'MEDICAL_STAFF', matching a
-- typo in app/models/enums/user_role.py: `gitr = "MEDICAL_STAFF"`).
-- We insert the DB label ('gitr') but keep human-readable names/emails.
INSERT INTO users (
    id, full_name, email, password_hash, role, selection_id,
    is_active, registration_status, created_at, updated_at
)
SELECT
    gen_random_uuid(),
    initcap(replace(r.display_name, '_', ' ')) || ' - ' || s.name,
    lower(r.display_name) || '_' || lower(s.code) || '@fifateamhub.test',
    'scrypt:32768:8:1$TSdtNkA5EuvSmuM4$bbf87efe84d370282a7d696b381534ca82873c526690ac887999e8f6cad95566320d784447bc302393f5731237c79292bfecf41c0a670ecd352216d0d3e63b7d',
    r.enum_value::userrole,
    s.id,
    true,
    'APPROVED'::registrationstatus,
    now(),
    now()
FROM selection s
CROSS JOIN (VALUES
    ('ATHELETE', 'ATHELETE'),
    ('AUDITOR', 'AUDITOR'),
    ('TECHNICAL_STAFF', 'TECHNICAL_STAFF'),
    ('MEDICAL_STAFF', 'gitr'),
    ('ORGANIZER', 'ORGANIZER')
) AS r(display_name, enum_value)
WHERE s.code IN ('BRA', 'ARG', 'FRA')
ON CONFLICT (email) DO NOTHING;
