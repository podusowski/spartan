import importlib
import logging


def import_module(workout, module_name='activity'):
    logging.debug('workout type: {}'.format(workout.activity_type))

    full_module_name = 'activities.{}.{}'.format(workout.activity_type, module_name)
    return importlib.import_module(full_module_name)
