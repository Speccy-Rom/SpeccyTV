QUERIES = {
    'average_movies_per_user': (
        'select avg(movies_watched) '
        'from ( '
        'select count(movie_id) as movies_watched '
        'from views '
        'group by user_id '
        '   ) as movies_count;'
    ),
    'average_view_times': 'select avg(viewed_frame) from views;',
    'top_20_users_by_total_view_time': (
        'select user_id, sum(viewed_frame) as view_time '
        'from views '
        'group by user_id '
        'order by view_time desc '
        'limit 20;'
    ),
    'top_20_movies_by_view_time': (
        'select movie_id, max(viewed_frame) as view_time '
        'from views '
        'group by movie_id '
        'order by view_time desc '
        'limit 20;'
    ),
    'unique_movies_count': 'select count(distinct movie_id) from views;',
    'unique_users_count': 'select count(distinct user_id) from views;'
}
