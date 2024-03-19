from datetime import datetime

import smtplib, ssl
import mimetypes
from email.message import EmailMessage
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

now = datetime.now()
mdp ="egaamsfizlsqanzj"
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

def send_mail(subject, content):

    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = "borgia.bellatores@gmail.com"
    msg["To"] = "borgia.bellatores@gmail.com"


    context=ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
        smtp.starttls(context=context)
        smtp.login(msg["From"], mdp)
        smtp.send_message(msg)

def send_mail_html(subject, html_table=None):

    # mime_type, _ = mimetypes.guess_type(file)
    # # mime_type, mime_subtype = mime_type.split('/')

    msg = MIMEMultipart()
    # msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = "borgia.bellatores@gmail.com"
    msg["To"] = "borgia.bellatores@gmail.com"

    if html_table is not None:
        msg.attach(MIMEText(html_table, 'html'))

    context=ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
        smtp.starttls(context=context)
        smtp.login(msg["From"], mdp)
        smtp.send_message(msg)


def send_mail_file(subject, content=None, file=None):

    # mime_type, _ = mimetypes.guess_type(file)
    # # mime_type, mime_subtype = mime_type.split('/')

    msg = EmailMessage()
    if content is not None:
        msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = "borgia.bellatores@gmail.com"
    msg["To"] = "borgia.bellatores@gmail.com"

    if file is not None:
        with open(file, 'rb') as content_file:
            content = content_file.read()
            msg.add_attachment(content, maintype='application', subtype= (file.split('.')[1]), filename=file)

    # print(msg)

    context=ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
        smtp.starttls(context=context)
        smtp.login(msg["From"], mdp)
        smtp.send_message(msg)
