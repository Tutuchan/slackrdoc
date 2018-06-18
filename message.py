# -*- coding: utf-8 -*-
"""
Python Slack Message class for use with the RDocumentation bot
"""
import json



class Message(object):
    """
    Instanciates a Message object to create and manage
    Slack RDocumentation messages.
    """
    def __init__(self):
        super(Message, self).__init__()
        self.channel = ""
        self.timestamp = ""
        self.text = ""
        self.attachments = []

    def create_attachments(self, description, url, fun):
        """
        Create the attachment for the function documentation.
        :param description: String, a short description of the function
        :param url: String, the full URL to the documentation
        :param fun: String, the fully qualified function name (package::function())
        :return: Nothing, the attachments fields is updated.
        """
        actions = [{"name": "visit", "type": "button", "text": "View documentation", "url": url}]
        self.attachments = [{"fallback": url, "title": fun, "text": description, "attachment_type": "default", "actions": actions}]
