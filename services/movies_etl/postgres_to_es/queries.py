LAST_FW_QUERY = "SELECT id FROM content.film_work WHERE modified > %s ORDER BY modified;"
LAST_PERSON_QUERY = "SELECT id FROM content.person WHERE modified > %s ORDER BY modified;"
LAST_GENRE_QUERY = "SELECT id FROM content.genre WHERE modified > %s ORDER BY modified;"

PERSON_FW_QUERY = '''
SELECT DISTINCT fw.id
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
WHERE pfw.person_id IN %s; 
'''

GENRE_FW_QUERY = '''
SELECT DISTINCT fw.id
FROM content.film_work fw
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
WHERE gfw.genre_id IN %s; 
'''

FW_QUERY = '''
SELECT
    fw.id as fw_id, 
    fw.title, 
    fw.description, 
    fw.rating, 
    fw.type, 
    fw.creation_date, 
    fw.modified, 
    pfw.role as person_role, 
    p.id as person_id, 
    p.full_name as person_name,
    g.id as genre_id,
    g.name as genre_name,
    f.id as file_id,
    f.file_path as file_path,
    f.video_width as video_width
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
LEFT JOIN content.file_film_work ffw ON ffw.film_work_id = fw.id
LEFT JOIN content.file f ON f.id = ffw.file_id
WHERE fw.id IN %s; 
'''

PERSON_QUERY = '''
SELECT
    p.id as person_id,
    p.full_name as person_name,
    pfw.role as person_role,
    fw.id as fw_id,
    fw.title as fw_title,
    fw.rating as fw_rating,
    fw.type as fw_type
FROM content.person p
LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
WHERE p.id IN %s; 
'''


GENRE_QUERY = '''
SELECT
    g.id as genre_id,
    g.name as genre_name,
    g.description as genre_description
FROM content.genre g
WHERE g.id IN %s; 
'''
