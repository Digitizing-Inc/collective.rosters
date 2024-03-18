from AccessControl import getSecurityManager
from AccessControl.Permissions import use_mailhost_services
from plone.registry.interfaces import IRegistry
from plone.restapi import _
from plone.restapi.bbb import IMailSchema
from plone.restapi.bbb import ISiteSchema
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from smtplib import SMTPException
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides
from email.utils import formataddr
from email.utils import getaddresses
from email.mime.multipart import MIMEMultipart

import plone

try:
    # Products.MailHost has a patch to fix quoted-printable soft line breaks.
    # See https://github.com/zopefoundation/Products.MailHost/issues/35
    from Products.MailHost.MailHost import message_from_string
except ImportError:
    # If the patch is ever removed, we fall back to the standard library.
    from email import message_from_string

class EmailSendAdvancePost(Service):

    def reply(self):
        data = json_body(self.request)

        send_to_address = data.get("to", None)
        send_bcc_address = data.get("bcc", None)
        send_cc_address = data.get("cc", None)
        sender_from_address = data.get("from", None)
        message = data.get("message", None)
        sender_fullname = data.get("name", "")
        subject = data.get("subject", "")

        recipients = [send_to_address]
        if send_bcc_address is not None:
            recipients += [formataddr(addr) for addr in getaddresses((send_bcc_address, ))]

        if not send_to_address and not send_bcc_address and not send_cc_address:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="BadRequest",
                    message='Missing "to", "bcc" or "cc" parameters. Atleast 1 should be present',
                )
            )

        if not sender_from_address:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="BadRequest",
                    message='Missing "from" parameter',
                )
            )

        if not message:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="BadRequest",
                    message='Missing "message" parameter',
                )
            )

        overview_controlpanel = getMultiAdapter(
            (self.context, self.request), name="overview-controlpanel"
        )
        if overview_controlpanel.mailhost_warning():
            self.request.response.setStatus(400)
            return dict(
                error=dict(type="BadRequest", message="MailHost is not configured.")
            )

        sm = getSecurityManager()
        if not sm.checkPermission(use_mailhost_services, self.context):
            pm = getToolByName(self.context, "portal_membership")
            if bool(pm.isAnonymousUser()):
                self.request.response.setStatus(401)
                error_type = "Unauthorized"
            else:
                self.request.response.setStatus(403)
                error_type = "Forbidden"
            return dict(error=dict(type=error_type, message=message))

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        from_address = mail_settings.email_from_address
        encoding = registry.get("plone.email_charset", "utf-8")
        host = getToolByName(self.context, "MailHost")
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
        portal_title = site_settings.site_title

        if not subject:
            if not sender_fullname:
                subject = self.context.translate(
                    _(
                        "A portal user via ${portal_title}",
                        mapping={"portal_title": portal_title},
                    )
                )
            else:
                subject = self.context.translate(
                    _(
                        "${sender_fullname} via ${portal_title}",
                        mapping={
                            "sender_fullname": sender_fullname,
                            "portal_title": portal_title,
                        },
                    )
                )

        message_intro = self.context.translate(
            _(
                "You are receiving this mail because ${sender_fullname} sent this message via the site ${portal_title}:",  # noqa
                mapping={
                    "sender_fullname": sender_fullname or "a portal user",
                    "portal_title": portal_title,
                },
            )
        )


        message = message_from_string(message)
        message["Reply-To"] = sender_from_address
        if send_to_address  is not None:
            message["To"] = formataddr((send_to_address, send_to_address))
        if send_cc_address  is not None:
            message["Cc"] = formataddr((send_cc_address, send_cc_address))
        if send_bcc_address  is not None:
            message["Bcc"] = formataddr((send_bcc_address, send_bcc_address))
        try:
            host.send(
                message,
                None,
                from_address,
                subject=subject,
                charset=encoding,
            )

        except (SMTPException, RuntimeError):
            plone_utils = getToolByName(self.context, "plone_utils")
            exception = plone_utils.exceptionString()
            message = f"Unable to send mail: {exception}"

            self.request.response.setStatus(500)
            return dict(error=dict(type="InternalServerError", message=message))

        return self.reply_no_content()