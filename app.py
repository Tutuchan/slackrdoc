# -*- coding: utf-8 -*-
"""
A routing layer for the RDocumentation bot, heavily inspired by the Python
[onboarding bot tutorial](https://github.com/slackapi/Slack-Python-Onboarding-Tutorial)
"""
import json
import bot
import re
from flask import Flask, request, make_response, render_template
import sys

pyBot = bot.Bot()
slack = pyBot.client

app = Flask(__name__)


def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.

    Parameters
    ----------
    event_type : str
        type of event received from Slack
    slack_event : dict
        JSON response from a Slack reaction event

    Returns
    ----------
    obj
        Response object with 200 - ok or 500 - No Event Handler error

    """
    team_id = slack_event["team_id"]
    if event_type == "message":
        if slack_event["event"]["channel_type"] in ["channel", "group"]:
            if "text" in slack_event["event"] and slack_event["event"]["text"] is not None:
                event_id = slack_event["event_id"]
                if not pyBot.check_event_id(event_id):
                    try:
                        event_text = slack_event["event"]["text"]
                        match = re.search(r"\?(?P<package>\w+)::(?P<function>\w+)", event_text)
                        if match:
                            print(slack_event)
                            channel_id = slack_event["event"]["channel"]
                            # if message comes from a thread, reply to the thread
                            # otherwise, create a new thread 
                            if "thread_ts" in slack_event["event"]:
                                thread_id = slack_event["event"]["thread_ts"] 
                            else:
                                thread_id = slack_event["event"]["ts"] 
                            pkg = match.group('package')
                            fun = match.group('function')
                            pyBot.update_client(team_id)
                            pyBot.documentation_message(pkg, fun, channel_id, thread_id)
                            pyBot.store_event_id(event_id)
                            return make_response("Documentation message sent", 200,)
                    except Exception as err:
                        print(err)
                        print(slack_event)

    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/install", methods=["GET"])
def pre_install():
    """This route renders the installation page with 'Add to Slack' button."""
    # Since we've set the client ID and scope on our Bot object, we can change
    # them more easily while we're developing our app.
    client_id = pyBot.oauth["client_id"]
    scope = pyBot.oauth["scope"]
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    """
    This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    code_arg = request.args.get('code')
    # The bot's auth method to handles exchanging the code for an OAuth token
    pyBot.auth(code_arg)
    return render_template("thanks.html")


@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.data)

    # ============= Slack URL Verification ============ #
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True)
