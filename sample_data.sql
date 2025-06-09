-- Sample Data for Helium Localization Management
-- Execute this in your Supabase SQL editor after running the schema setup
INSERT INTO translation_keys (key, category, description)
VALUES (
        'greeting.hello',
        'greetings',
        'Standard hello greeting'
    ),
    (
        'greeting.goodbye',
        'greetings',
        'Standard goodbye greeting'
    );
INSERT INTO translations (
        translation_key_id,
        language_code,
        value,
        updated_by
    )
SELECT tk.id,
    'en',
    CASE
        tk.key
        WHEN 'greeting.hello' THEN 'Hello'
        WHEN 'greeting.goodbye' THEN 'Goodbye'
    END,
    'system'
FROM translation_keys tk;
INSERT INTO translations (
        translation_key_id,
        language_code,
        value,
        updated_by
    )
SELECT tk.id,
    'es',
    CASE
        tk.key
        WHEN 'greeting.hello' THEN 'Hola'
        WHEN 'greeting.goodbye' THEN 'Adiós'
    END,
    'system'
FROM translation_keys tk;
INSERT INTO translations (
        translation_key_id,
        language_code,
        value,
        updated_by
    )
SELECT tk.id,
    'fr',
    CASE
        tk.key
        WHEN 'greeting.hello' THEN 'Bonjour'
        WHEN 'greeting.goodbye' THEN 'Au revoir'
    END,
    'system'
FROM translation_keys tk;
SELECT tk.key,
    tk.category,
    STRING_AGG(
        t.language_code || ': ' || t.value,
        ' | '
        ORDER BY t.language_code
    ) as translations
FROM translation_keys tk
    LEFT JOIN translations t ON tk.id = t.translation_key_id
GROUP BY tk.id,
    tk.key,
    tk.category
ORDER BY tk.key;
SELECT tk.key,
    tk.category,
    COUNT(t.id) as translation_count,
    STRING_AGG(
        t.language_code || ': ' || t.value,
        ' | '
        ORDER BY t.language_code
    ) as translations
FROM translation_keys tk
    LEFT JOIN translations t ON tk.id = t.translation_key_id
GROUP BY tk.id,
    tk.key,
    tk.category
ORDER BY tk.category,
    tk.key;