from tests.utils import ClientTestCase


class ExplorerTestCase(ClientTestCase):
    def test_showing_empty_explorer_page(self):
        self.get('/explorer')
