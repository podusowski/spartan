import pytest

from tests.utils import *
from tests import utils
from training import units

from tests import test_strength


class GoalsTestCase(ClientTestCase):
    _strength_workout = utils.strength_workout

    def _set_goal(self, name, volume):
        return self.post("/statistics/add_goal", {'name': name, 'volume': volume})

    def test_create_goal(self):
        workout_statistics_page = self._set_goal("push-up", 100)

        goal = workout_statistics_page.context["goal"]
        assert 100 == goal.volume
        assert units.Volume(0) == goal.progress

    def test_both_user_sets_some_goals(self):
        """
        Make sure user get its own goals despite the fact that other user
        created one for itself.
        """

        self._set_goal("push-up", 100)

        self.switch_user(self.other_user)

        self._set_goal("push-up", 50)

        self.switch_user(self.user)

        workout_statistics_page = self.get("/statistics/workout/push-up")

        goal = workout_statistics_page.context["goal"]
        assert 100 == goal.volume
        assert units.Volume(0) == goal.progress

    def test_its_improssible_to_set_a_goal_without_a_name(self):
        with pytest.raises(AttributeError):
            self._set_goal("", 100)

    def test_goal_value_must_have_positive_value(self):
        with pytest.raises(AttributeError):
            self._set_goal("push-up", 0)
