"""
/*********************************************************************************/
 *  The MIT License (MIT)                                                         *
 *                                                                                *
 *  Copyright (c) 2014 EOX IT Services GmbH                                       *
 *                                                                                *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy  *
 *  of this software and associated documentation files (the "Software"), to deal *
 *  in the Software without restriction, including without limitation the rights  *
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell     *
 *  copies of the Software, and to permit persons to whom the Software is         *
 *  furnished to do so, subject to the following conditions:                      *
 *                                                                                *
 *  The above copyright notice and this permission notice shall be included in    *
 *  all copies or substantial portions of the Software.                           *
 *                                                                                *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR    *
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,      *
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE   *
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER        *
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, *
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE *
 *  SOFTWARE.                                                                     *
 *                                                                                *
 *********************************************************************************/
"""

from datetime import datetime
from getpass import getuser

from airflow import DAG
from airflow.operators import DownloadSceneList
from airflow.operators import ExtractSceneList
from airflow.operators import UpdateSceneList

import config as CFG
import config.landsat8 as LANDSAT8

landsat8_scene_list = DAG(
    LANDSAT8.id + '_Scene_List',
    description='DAG for downloading, extracting, and importing scene_list.gz '
                'into postgres db',
    default_args={
        "start_date": datetime(2017, 1, 1),
        "owner": getuser(),
        "depends_on_past": False,
        "provide_context": True,
        "email": ["xyz@xyz.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 0,  # TODO: change back to 1
        "max_threads": 1,
        "download_dir": LANDSAT8.download_dir,
        "download_url": LANDSAT8.download_url,
    },
    dagrun_timeout=LANDSAT8.dagrun_timeout,
    schedule_interval=LANDSAT8.dag_schedule_interval,
    catchup=False
)

# more info on Landsat products on AWS at:
# https://aws.amazon.com/public-datasets/landsat/
download_scene_list_gz = DownloadSceneList(
    task_id='download_scene_list_gz',
    dag=landsat8_scene_list
)

extract_scene_list = ExtractSceneList(
    task_id='extract_scene_list',
    dag=landsat8_scene_list
)

update_scene_list_db = UpdateSceneList(
    task_id='update_scene_list',
    pg_dbname=CFG.landsat8_postgresql_credentials['dbname'],
    pg_hostname=CFG.landsat8_postgresql_credentials['hostname'],
    pg_port=CFG.landsat8_postgresql_credentials['port'],
    pg_username=CFG.landsat8_postgresql_credentials['username'],
    pg_password=CFG.landsat8_postgresql_credentials['password'],
    dag=landsat8_scene_list
)

download_scene_list_gz.set_downstream(extract_scene_list)
extract_scene_list.set_downstream(update_scene_list_db)
