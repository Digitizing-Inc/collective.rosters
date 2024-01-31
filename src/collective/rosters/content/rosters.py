from plone import schema
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobImage
from plone.schema.email import Email
from plone.supermodel import model
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.radio import RadioFieldWidget
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.row import DictRow
from plone.autoform.form import AutoExtensibleForm
from z3c.form import form
from zope import interface

class ITableRowSchema(interface.Interface):
    one = schema.TextLine(title=u"One")
    two = schema.TextLine(title=u"Two")
    three = schema.TextLine(title=u"Three")

class IRosters(model.Schema):
    """Dexterity-Schema for Rosters"""

    # directives.widget(type_of_talk=RadioFieldWidget)
    # type_of_talk = schema.Choice(
    #     title='Type of rosters',
    #     values=['Rosters', 'Training', 'Keynote'],
    #     required=True,
    # )

    details = RichText(
        title='Details',
        description='Description of the rosters (max. 2000 characters)',
        max_length=2000,
        required=True,
    )

    directives.widget(table=DataGridFieldFactory)
    table = schema.List(
        title=u"Table",
        value_type=DictRow(
            title=u"tablerow",
            schema=ITableRowSchema,
        ),
        required=False,
    )

    # directives.widget(audience=CheckBoxFieldWidget)
    # audience = schema.Set(
    #     title='Audience',
    #     value_type=schema.Choice(
    #         values=['Beginner', 'Advanced', 'Professional'],
    #     ),
    #     required=False,
    # )

    speaker = schema.TextLine(
        title='Speaker',
        description='Name (or names) of the speaker',
        required=False,
    )

    # company = schema.TextLine(
    #     title='Company',
    #     required=False,
    # )

    # email = Email(
    #     title='Email',
    #     description='Email adress of the speaker',
    #     required=False,
    # )

    # website = schema.TextLine(
    #     title='Website',
    #     required=False,
    # )

    # twitter = schema.TextLine(
    #     title='Twitter name',
    #     required=False,
    # )

    # github = schema.TextLine(
    #     title='Github username',
    #     required=False,
    # )

    # image = NamedBlobImage(
    #     title='Image',
    #     description='Portrait of the speaker',
    #     required=False,
    # )

    # speaker_biography = RichText(
    #     title='Speaker Biography (max. 1000 characters)',
    #     max_length=1000,
    #     required=False,
    # )


@implementer(IRosters)
class Rosters(Container):
    """Rosters instance class"""