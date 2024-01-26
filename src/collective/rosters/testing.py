# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.rosters


class CollectiveRostersLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.rosters)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.rosters:default")


COLLECTIVE_ROSTERS_FIXTURE = CollectiveRostersLayer()


COLLECTIVE_ROSTERS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_ROSTERS_FIXTURE,),
    name="CollectiveRostersLayer:IntegrationTesting",
)


COLLECTIVE_ROSTERS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_ROSTERS_FIXTURE,),
    name="CollectiveRostersLayer:FunctionalTesting",
)


COLLECTIVE_ROSTERS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_ROSTERS_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="CollectiveRostersLayer:AcceptanceTesting",
)
