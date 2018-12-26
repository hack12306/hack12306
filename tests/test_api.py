# encoding: utf8

import pytest
from hack12306.api import TrainApi


class TestTrainApi(object):
    """
    测试12306 API
    """

    @pytest.fixture()
    def train_api(self):
        return TrainApi()

    def test_query_dishonest(self, train_api):
        result = train_api.query_dishonest()
        assert result['status'] is True
