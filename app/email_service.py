import smtplib
from email.message import EmailMessage
from typing import TypedDict

from jinja2 import Environment, FileSystemLoader

from app.config import EmailConfig


class SendEmailArgs(TypedDict):
    subject: str
    to: str
    template: str
    variables: dict[str, str]


class EmailService:
    def __init__(self, config: EmailConfig) -> None:
        self.config = config
        self.smtp = smtplib.SMTP(host=config.smtp_host, port=config.smtp_port)

        if config.smtp_tls:
            self.smtp.starttls()

        self.environment = Environment(loader=FileSystemLoader("templates/"))
        self.smtp.login(config.smtp_username, config.smtp_password)

    def __del__(self):
        self.smtp.quit()

    def send_email(self, **args: SendEmailArgs):
        template = self.environment.get_template(args["template"])
        content = template.render(args["variables"])

        email = EmailMessage()
        email.set_content(content, "html")
        email["Subject"] = args["subject"]
        email["From"] = self.config.sender
        email["To"] = args["to"]

        self.smtp.send_message(email)
