# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the RDocumentation app
"""
import os
import message
import parser
import psycopg2
from psycopg2 import sql
import sys
from slackclient import SlackClient

DATABASE_URL = os.environ['DATABASE_URL']


class Bot(object):
    """ Instanciates a Bot object to handle Slack RDocumentation interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "RDocumentation"
        self.emoji = ":book:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        self.client = SlackClient("")

    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.

        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token

        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        team_id = auth_response["team_id"]
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to Postgre

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS authed_teams (id serial PRIMARY KEY, team_id varchar, bot_token varchar);")
        cur.execute(sql.SQL("select bot_token FROM authed_teams WHERE team_id = {}").format(sql.Literal(team_id)))
        db_token = cur.fetchone()
        if db_token is None:
            db_token = auth_response["bot"]["bot_access_token"]
            cur.execute(sql.SQL("INSERT INTO authed_teams VALUES ({}, {})").format(sql.Literal(team_id), sql.Literal(db_token)))
            conn.commit()

        cur.close()
        conn.close()
        self.client = SlackClient(db_token)

    def documentation_message(self, package, fun, channel):
        """
        Create and send a message containing a short description of the function
        and a link to the RDocumentation website

        Parameters
        ----------
        package : str
            name of the R package
        function : str
            name of the R function in the package
        channel : str
            id of the Slack channel where to post the message

        """

        desc = parser.Parser(package, fun)
        desc.retrieve_desc()

        msg = message.Message()
        fun_str = package + '::' + fun + '()'
        msg.create_attachments(desc.text, desc.url, fun_str)

        post_message = self.client.api_call("chat.postMessage",
                                            channel=channel,
                                            icon_emoji=self.emoji,
                                            attachments=msg.attachments
                                            )
