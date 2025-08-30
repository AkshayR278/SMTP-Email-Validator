import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import AsyncMessage
from validator import validate_email_address

class EmailValidationHandler(AsyncMessage):
    async def handle_MAIL(self, server, session, envelope, address, mail_options):
        if not validate_email_address(address):
            return '550 5.1.3 Bad sender address syntax'
        envelope.mail_from = address
        return '250 OK'

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if not validate_email_address(address):
            return '550 5.1.3 Bad recipient address syntax'
        envelope.rcpt_tos.append(address)
        return '250 OK'

if __name__ == "__main__":
    controller = Controller(EmailValidationHandler(), hostname='127.0.0.1', port=8025)
    controller.start()
    print("SMTP server running on port 8025")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        controller.stop()
