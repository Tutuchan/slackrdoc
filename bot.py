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

# The Postgre database URL to store the id of the teams and their OAuth tokens.
DATABASE_URL = os.environ['DATABASE_URL']

class Bot(object):
    """ Instanciates a Bot object to handle Slack RDocumentation interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "RDocumentation"
        self.emoji = ":book:"
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      "scope": "bot,channels:history,groups:history"}
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

        if "team_id" in auth_response:
            team_id = auth_response["team_id"]
            # To keep track of authorized teams and their associated OAuth tokens,
            # we will save the team ID and bot tokens to Postgre

            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS authed_teams (id serial PRIMARY KEY, team_id varchar, bot_token varchar(256));")
            cur.execute(sql.SQL("select bot_token FROM authed_teams WHERE team_id = {}").format(sql.Literal(team_id)))
            db_token = cur.fetchone()

            if db_token is not None:
                cur.execute(sql.SQL("DELETE FROM authed_teams WHERE team_id = {}").format(sql.Literal(team_id)))
                conn.commit()
            db_token = auth_response["bot"]["bot_access_token"]
            cur.execute(sql.SQL("INSERT INTO authed_teams (team_id, bot_token) VALUES ({}, {})").format(sql.Literal(team_id), sql.Literal(db_token)))
            conn.commit()
            cur.close()
            conn.close()
            self.client = SlackClient(db_token)
        else:
            print("Authentication failed!\n")
            print(auth_response)

    def documentation_message(self, package, fun, channel):
        """
        Create and send a message containing a short description of the function
        and a link to the RDocumentation website

        Parameters
        ----------
        package : str
            name of the R package
        fun : str
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
        print(post_message)

    def update_client(self, team_id):
        """
        Update the Slack client object with the OAuth token associated to the team associated with the event
        :param team_id: the id of the team requesting the message
        :return: Nothing, the client field is updated with the correct token
        """

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(sql.SQL("select bot_token FROM authed_teams WHERE team_id = {}").format(sql.Literal(team_id)))
        db_token = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        self.client = SlackClient(db_token)

