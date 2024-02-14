from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import implementer

class IEmailVerification(model.Schema):
    """Dexterity-Schema for EmailVerification"""


@implementer(IEmailVerification)
class EmailVerification(Container):
    """EmailVerification instance class"""