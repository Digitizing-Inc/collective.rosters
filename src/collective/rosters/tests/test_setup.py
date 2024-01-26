# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.rosters.testing import (  # noqa: E501
    COLLECTIVE_ROSTERS_INTEGRATION_TESTING,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that collective.rosters is properly installed."""

    layer = COLLECTIVE_ROSTERS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if collective.rosters is installed."""
        self.assertTrue(self.installer.is_product_installed("collective.rosters"))

    def test_browserlayer(self):
        """Test that ICollectiveRostersLayer is registered."""
        from collective.rosters.interfaces import ICollectiveRostersLayer
        from plone.browserlayer import utils

        self.assertIn(ICollectiveRostersLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_ROSTERS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("collective.rosters")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.rosters is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("collective.rosters"))

    def test_browserlayer_removed(self):
        """Test that ICollectiveRostersLayer is removed."""
        from collective.rosters.interfaces import ICollectiveRostersLayer
        from plone.browserlayer import utils

        self.assertNotIn(ICollectiveRostersLayer, utils.registered_layers())
