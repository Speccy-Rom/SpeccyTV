from itertools import chain


def get_create_partition_cmd(table_name, modulus, remainder):
    partition_name = _get_partition_name(table_name, remainder)
    return f"""CREATE TABLE IF NOT EXISTS content.{partition_name}
                PARTITION OF content.{table_name} 
                FOR VALUES WITH (modulus {modulus}, remainder {remainder});"""


def get_create_partition_index_cmd(table_name, remainder, index_col):
    partition_name = _get_partition_name(table_name, remainder)
    return f"""CREATE UNIQUE INDEX IF NOT EXISTS {partition_name}_{index_col}_idx ON content.{partition_name}({index_col});"""


def get_drop_partition_cmd(table_name, remainder):
    partition_name = _get_partition_name(table_name, remainder)
    return f"""DROP TABLE content.{partition_name}"""


def _get_partition_name(table_name, remainder):
    return f'{table_name}_m{remainder}'


def get_create_users_partitions_cmds(partitions_num):
    return chain.from_iterable(
        (get_create_partition_cmd('users', partitions_num, remainder),
         get_create_partition_index_cmd('users', remainder, 'email')) for remainder in range(partitions_num)
    )


def get_create_user_permission_partitions_cmds(partitions_num):
    return [get_create_partition_cmd('user_permission', partitions_num, remainder) for remainder in range(partitions_num)]
