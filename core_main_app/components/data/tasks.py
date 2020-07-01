""" Data tasks
"""

from bson.objectid import ObjectId
from celery import shared_task
from celery.result import AsyncResult

from core_main_app.components.data import api as data_api
from core_main_app.components.template import api as template_api
from core_main_app.components.user import api as user_api
from core_main_app.utils.pagination.mongoengine_paginator.paginator import (
    MongoenginePaginator,
)


@shared_task
def async_migration_task(data_list, template_id, user_id, migrate):
    """ Async task which perform a migration / validation of the data list for the given target template id

    Args:
        data_list:
        template_id:
        user_id:
        migrate: (boolean) Perform the migration

    Return:
        {"valid": ["id"...], "wrong": ["id"...]}
    """
    success = []
    errors = []
    current_progress = 0
    total_data = len(data_list)

    try:
        target_template = template_api.get(template_id)
        user = user_api.get_user_by_id(user_id)

        for data_id in data_list:
            data = data_api.get_by_id(data_id, user=user)
            # modify the data temporarily with the new targeted template
            data.template = target_template

            try:
                # save the new template for the data if the migration is True
                if migrate:
                    data_api.upsert(data, user)
                else:
                    # check if the data is valid
                    data_api.check_xml_file_is_valid(data)

                success.append(str(data.id))
            except Exception as e:
                errors.append(str(data.id))
            finally:
                # increase the current progress and update the task state
                current_progress += 1
                async_migration_task.update_state(
                    state="PROGRESS",
                    meta={"current": current_progress, "total": total_data},
                )
    except Exception as e:
        async_migration_task.update_state(
            state="ABORT", meta={"current": current_progress, "total": total_data}
        )
        raise Exception(f"Something went wrong: {str(e)}")

    return {"valid": success, "wrong": errors}


@shared_task
def async_template_migration_task(templates, target_template_id, user_id, migrate):
    """ Async task which perform a migration / validation of all the data which belong to the given template id list

    Args:
        templates:
        target_template_id:
        user_id
        migrate: (boolean) Perform the migration

    Return:
        {"valid": <number>, "wrong": <number>}
    """
    # get the data list to check
    current_data_progress = 0
    current_template_progress = -1
    total_data = 0
    total_template = len(templates)
    success = []
    error = []
    try:
        if target_template_id and total_template > 0:
            # get the user
            user = user_api.get_user_by_id(user_id)
            # get the target template
            target_template = template_api.get(target_template_id)

            for template_id in templates:

                # increase the number of processed template
                current_template_progress += 1
                # rest de number of data
                current_data_progress = 0

                # get a QuerySet of all the data with the given template
                data_list = data_api.execute_query(
                    {"template": ObjectId(template_id)}, user=user
                )

                total_data = data_list.count()

                # extract the data id from the list
                data_list_id = data_list.values_list("id")

                for data_id in data_list_id:

                    # get the data
                    data = data_api.get_by_id(data_id, user)

                    # modify the data temporarily with the new targeted template
                    data.template = target_template
                    # check if the data is valid
                    try:
                        # save the new template for the data if the migration is True
                        if migrate:
                            data_api.upsert(data, user)
                        else:
                            data_api.check_xml_file_is_valid(data)

                        success.append(str(data.id))
                    except Exception as e:
                        error.append(str(data.id))
                    finally:
                        # increase the current progress and update the task state
                        current_data_progress += 1
                        async_template_migration_task.update_state(
                            state="PROGRESS",
                            meta={
                                "template_current": current_template_progress,
                                "template_total": total_template,
                                "data_current": current_data_progress,
                                "data_total": total_data,
                            },
                        )

            return {"valid": success, "wrong": error}

        else:
            async_template_migration_task.update_state(
                state="ABORT",
                meta={
                    "template_current": current_template_progress,
                    "template_total": total_template,
                    "data_current": current_data_progress,
                    "data_total": total_data,
                },
            )
            raise Exception(
                "Wrong template id."
                if not target_template_id
                else "Please provide template id."
            )
    except Exception as e:
        async_template_migration_task.update_state(
            state="ABORT",
            meta={
                "template_current": current_template_progress,
                "template_total": total_data,
                "data_current": current_data_progress,
                "data_total": total_data,
            },
        )
        raise Exception(f"Something went wrong: {str(e)}")


def get_task_progress(task_id):
    """ Get task status for the given task id

    Args:
        task_id:

    Return:
        {
            'state': PENDING | PROGRESS | SUCCESS,
            'details': result (for SUCCESS) | null (for PENDING) | { PROGRESS info }
        }
    """
    result = AsyncResult(task_id)
    response_data = {
        "state": result.state,
        "details": result.info,
    }
    return response_data


def get_task_result(task_id):
    """ Get task result for the given task id

    Args:
        task_id:

    Return: {
                "valid": ["data_id_1", "data_id_2" ...],
                "wrong": ["data_id_3", "data_id_4" ...]
            }
    """
    result = AsyncResult(task_id).result
    return result
