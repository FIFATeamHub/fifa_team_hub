-- Seed: one document of each type per selection (Brazil, Argentina, France).
-- Depends on backend/scripts/seed_selections_users.sql having already run
-- (uses the seeded users as uploaded_by, matched by role).
-- Safe to re-run: skips (selection, type) pairs that already exist.

INSERT INTO document (
    id, selection_id, uploaded_by, type, original_name, storage_path,
    status, created_at, storage_url
)
SELECT
    gen_random_uuid(),
    s.id,
    u.id,
    d.doc_type::typedocument,
    d.doc_type || '_' || s.code || '.pdf',
    'seed/' || lower(s.code) || '/' || lower(d.doc_type) || '.pdf',
    'PENDING',
    now(),
    'https://storage.example.com/seed/' || lower(s.code) || '/' || lower(d.doc_type) || '.pdf'
FROM selection s
CROSS JOIN (VALUES
    ('PASSPORT', 'athelete'),
    ('CONVOCADO', 'organizer'),
    ('LAUDO_MEDICO', 'medical_staff'),
    ('RELATORIO_TATICO', 'technical_staff'),
    ('ESQUEMA_JOGADAS', 'technical_staff')
) AS d(doc_type, uploader_prefix)
JOIN users u
    ON u.email = d.uploader_prefix || '_' || lower(s.code) || '@fifateamhub.test'
WHERE s.code IN ('BRA', 'ARG', 'FRA')
  AND NOT EXISTS (
        SELECT 1 FROM document doc2
        WHERE doc2.selection_id = s.id
          AND doc2.type = d.doc_type::typedocument
  );