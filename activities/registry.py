import importlib
import logging

from django.apps import apps


def import_module(workout, module_name='activity'):
    logging.debug('workout type: {}'.format(workout.activity_type))

    full_module_name = 'activities.{}.{}'.format(workout.activity_type, module_name)
    return importlib.import_module(full_module_name)


def modules(submodule_name='local_statistics'):
    '''
    Gets all submodules of activities modules 
    '''

    for app in apps.get_app_configs():
        try:
            yield importlib.import_module('{}.local_statistics'.format(app.name))
        except ImportError as e:
            logging.debug('can\'t import app {}'.format(app.name))
