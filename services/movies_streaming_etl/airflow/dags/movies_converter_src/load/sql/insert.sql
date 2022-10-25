INSERT
    INTO
        file (
            id
            ,file_path
            ,resolution
            ,created
            ,modified
        )
    VALUES {}
        ON CONFLICT (id) DO NOTHING
