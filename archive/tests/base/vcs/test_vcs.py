
from unittest import TestCase

from gameta.base import VCS, vcs_interfaces


class TestVCSInterfaces(TestCase):
    def test_supported_vcs_interfaces(self):
        self.assertTrue(all(i in list(vcs_interfaces) for i in ['git']))
        for i in vcs_interfaces.values():
            self.assertTrue(issubclass(i, VCS))
