import asyncio
import logging
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message
from validator import validate_email_address

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class EmailValidationHandler(Message):
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

    async def handle_DATA(self, server, session, envelope):
        logger.info("Received message from %s to %s", envelope.mail_from, envelope.rcpt_tos)
        return '250 Message accepted for delivery'


async def run_server(hostname: str = '127.0.0.1', port: int = 8025) -> None:
    controller = Controller(EmailValidationHandler(), hostname=hostname, port=port)
    controller.start()
    logger.info("SMTP validation server is running at %s:%s", hostname, port)

    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        controller.stop()
        logger.info("SMTP validation server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
