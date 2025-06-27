from anymail.message import AnymailMessage


def send_email(subject:str, body:str, to:list[str], tags: list[str] | None = None):
    """Sends email

    Args:
        subject (str): The email's subject
        body (str): The email's body
        to (list[str]): The list of recipients each recipient has this format
            'Name Surname <email123@example.com>'
        tags (list[str], optional): Extra tags. Defaults to [].
    """
    message = AnymailMessage(
        subject=subject,
        body=body,
        to=to,
        tags=[] if tags is None else tags,
    )

    message.send()
