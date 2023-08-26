import datetime
import os
import uuid

import functions_framework
import pandas as pd
import requests
import sqlalchemy

"""
This cloud function will be auto executed by cloud scheduler each day [at 00:00 GMT+0]
"""


# Source: https://cloud.google.com/sql/docs/postgres/connect-functions # noqa: E501
def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    """Initializes a Unix socket connection pool for a Cloud SQL instance of Postgres."""  # noqa: E501
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_user = os.environ["DB_USER"]  # e.g. 'my-database-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-database-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
    unix_socket_path = os.environ[
        "INSTANCE_UNIX_SOCKET"
    ]  # e.g. '/cloudsql/project:region:instance'

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # postgresql+pg8000://<db_user>:<db_pass>@/<db_name>
        #                         ?unix_sock=<INSTANCE_UNIX_SOCKET>/.s.PGSQL.5432
        # Note:
        # Some drivers require the `unix_sock` query parameter to use a different key.
        # For example:
        # 'psycopg2' uses the path set to `host` in order to connect successfully.
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_sock": f"{unix_socket_path}/.s.PGSQL.5432"},
        ),
        # ...
    )
    return pool


def get_renamed(cat, patt=""):
    transformed_cat = ""
    if cat == "meditation":
        transformed_cat = "med"
    if cat == "exercise":
        transformed_cat = "exe"
    if cat == "reading":
        transformed_cat = "read"
    if patt == "taskcomp":
        return f"task_{transformed_cat}_completed"
    if patt == "actnum":
        return f"act_{transformed_cat}_num"
    if patt == "actuniq":
        return f"act_{transformed_cat}_nununique"


def get_task_data(conn):
    dt_now = datetime.datetime.now(datetime.timezone.utc).date()
    dt_yesterday = dt_now - datetime.timedelta(days=1)
    data = conn.execute(
        sqlalchemy.text(
            f"SELECT users_task_log.user_id, users_task_log.created_at, users_task_log.completed_at, tasks.activity_category FROM users_task_log INNER JOIN tasks ON (users_task_log.task_id = tasks.id) WHERE (users_task_log.created_at = '{dt_yesterday}T00:00:00+00:00'::timestamptz)"  # noqa: E501
        )
    ).fetchall()
    return data


def preprocessing_task_data(task_data):
    dict_transformed = {
        "user_id": [],
        "task_exe_completed": [],  # 0, 1, 1, 0
        "task_med_completed": [],
        "task_read_completed": [],
    }

    idx = 0
    idx_user_id = {}

    for data in task_data:
        if data[0] not in idx_user_id.keys():
            idx_user_id[data[0]] = idx
            dict_transformed["user_id"].append(data[0])
            # Init
            dict_transformed["task_exe_completed"].append(0)
            dict_transformed["task_med_completed"].append(0)
            dict_transformed["task_read_completed"].append(0)
            idx += 1

        dict_transformed[get_renamed(data[3], "taskcomp")][idx_user_id[data[0]]] = (
            1 if data[2] else 0
        )

    return pd.DataFrame.from_dict(dict_transformed)


def get_activity_data(conn):
    # Note: if user did activity even not finished it will auto create all task log (see: users/serializer.py) # noqa: E501
    dt_now = datetime.datetime.now(datetime.timezone.utc).date()
    dt_yesterday = dt_now - datetime.timedelta(days=1)
    data = conn.execute(
        sqlalchemy.text(
            f"SELECT users_activity_log.user_id, users_activity_log.activity_id, activities.category FROM users_activity_log INNER JOIN activities ON (users_activity_log.activity_id = activities.id) WHERE (users_activity_log.finished IS TRUE AND users_activity_log.play_at >= '{dt_yesterday}T00:00:00+00:00'::timestamptz AND users_activity_log.play_at < '{dt_now}T00:00:00+00:00'::timestamptz)"  # noqa: E501
        )
    ).fetchall()
    return data


def preprocessing_activity_data(activity_data):
    dict_transformed = {
        "user_id": [],
        "act_exe_num": [],
        "act_med_num": [],
        "act_read_num": [],
        "act_exe_nununique": [],
        "act_med_nununique": [],
        "act_read_nununique": [],
    }

    idx = 0
    # schema of data_user_id {
    #     "user_id": {
    #         "idx": 0,
    #         "exercise": [],
    #         "meditation": [],
    #         "reading": [],
    #     }
    # }
    data_user_id = {}

    for data in activity_data:
        if data[0] not in data_user_id.keys():
            # Init
            data_user_id[data[0]] = {}
            data_user_id[data[0]]["idx"] = idx
            data_user_id[data[0]]["exercise"] = []
            data_user_id[data[0]]["meditation"] = []
            data_user_id[data[0]]["reading"] = []
            dict_transformed["user_id"].append(data[0])
            dict_transformed["act_exe_num"].append(0)
            dict_transformed["act_med_num"].append(0)
            dict_transformed["act_read_num"].append(0)
            dict_transformed["act_exe_nununique"].append(0)
            dict_transformed["act_med_nununique"].append(0)
            dict_transformed["act_read_nununique"].append(0)
            idx += 1

        # act_<cat>_num handler
        dict_transformed[get_renamed(data[2], "actnum")][
            data_user_id[data[0]]["idx"]
        ] += 1

        # act_<cat>_nununique handler
        if data[1] not in data_user_id[data[0]][data[2]]:
            data_user_id[data[0]][data[2]].append(data[1])
            dict_transformed[get_renamed(data[2], "actuniq")][
                data_user_id[data[0]]["idx"]
            ] = len(data_user_id[data[0]][data[2]])

    return pd.DataFrame.from_dict(dict_transformed)


def get_streak_data(conn):
    data = conn.execute(
        sqlalchemy.text(
            "SELECT users_game_stats.user_id, users_game_stats.streak_current FROM users_game_stats"  # noqa: E501
        )
    ).fetchall()
    return data


def preprocessing_streak_data(streak_data):
    return pd.DataFrame(streak_data, columns=["user_id", "streak_current"])


@functions_framework.http
def collect_and_predict(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    # 1) Init data connection
    db = connect_unix_socket()

    # 2) Collect and preprocessing
    with db.connect() as conn:
        df_1 = preprocessing_task_data(get_task_data(conn))
        df_2 = preprocessing_activity_data(get_activity_data(conn))
        df_3 = preprocessing_streak_data(get_streak_data(conn))
        # Combine (merge with intersection)
        df_1_2 = pd.merge(df_1, df_2, how="inner", on=["user_id"])
        df_1_2_3 = pd.merge(df_1_2, df_3, how="inner", on=["user_id"])

    # 3) Data request preparation (without serialize for efficiency)
    list_features = [key for key in df_1_2_3.keys() if key != "user_id"]
    model_inputs = "{"
    for idx, key in enumerate(list_features):
        model_inputs += '"%s": %s' % (key, df_1_2_3[key].to_list())
        if idx != len(list_features) - 1:
            model_inputs += ","
    model_inputs += "}"

    # 4) Get predictions
    # Not suitable for large data (latency problem)
    endpoint = "https://improveyou-tfserving-v1-qguw2amrfq-uc.a.run.app/v1/models/urge-model:predict"  # noqa: E501
    # TODO: endpoint tf serving should be not publicity (unauthenticated) => change into authenticated (service to service) # noqa: E501
    data_request = '{"signature_name": "serving_default", "inputs": %s}' % (
        model_inputs
    )
    # See: https://github.com/tensorflow/serving/blob/master/tensorflow_serving/g3doc/api_rest.md # noqa: E501
    response = requests.post(endpoint, data=data_request).json()

    # 5) Processing data before insert into database
    values_insert = ""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for idx, predict in enumerate(response["outputs"]):
        urge_level = ""
        if 0 >= predict[1] and predict[1] < 0.20:
            urge_level = "very_low"
        elif 0.20 >= predict[1] and predict[1] < 0.40:
            urge_level = "low"
        elif 0.40 >= predict[1] and predict[1] < 0.60:
            urge_level = "medium"
        elif 0.60 >= predict[1] and predict[1] < 0.80:
            urge_level = "high"
        else:
            urge_level = "very_high"

        values_insert += "('%s'::uuid, '%s'::uuid, %f, '%s', '%s'::timestamptz)" % (
            uuid.uuid1(),
            df_1_2_3["user_id"][idx],
            predict[1],
            urge_level,
            now,
        )
        values_insert += "," if idx != len(response["outputs"]) - 1 else ""

    with db.connect() as conn:
        conn.execute(
            sqlalchemy.text(
                f"INSERT INTO users_recommendation_log (id, user_id, prediction, urge_level, issue_at) VALUES {values_insert}"  # noqa: E501
            )
        )
        conn.commit()

    return "Done!  -🔥🔥🔥 v1"
