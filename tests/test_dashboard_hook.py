import unittest
from unittest.mock import Mock

from app.ui.features.dashboard import use_dashboard
from app.ui.features.dashboard import DashboardRefreshers


class DashboardHookTests(unittest.TestCase):
    def test_result_exposes_services_and_refreshes_registered_views(self):
        services = [Mock() for _ in range(5)]
        result = use_dashboard(*services)
        refreshers = [Mock(), Mock(), Mock()]
        result.register_refreshers(DashboardRefreshers(todos=refreshers[0], notes=refreshers[1], work_board=refreshers[2]))
        result.refresh_all()
        for refresher in refreshers:
            refresher.assert_called_once_with()
        self.assertIs(result.todo_service, services[0])
        self.assertIs(result.comment_service, services[4])

    def test_result_exposes_work_item_lookup(self):
        services = [Mock() for _ in range(5)]
        services[3].get.return_value = "work-item"
        result = use_dashboard(*services)
        self.assertEqual(result.get_work_item("item-1"), "work-item")
        services[3].get.assert_called_once_with("item-1")


if __name__ == "__main__":
    unittest.main()
