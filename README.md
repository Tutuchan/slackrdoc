# slackrdoc

This is a simple Slack bot that listens to messages written in Slack for patterns like `<package>::<function>`, then
visits the [RDocumentation](https://www.rdocumentation.org/) page for this function. If such a function exists, it then
sends a message back to the Slack channel where the first message originated with a brief description of the function
and a link to the complete documentation.

## Installation

An instance of the bot is deployed on Heroku at https://slackrdoc.herokuapp.com/install. Just click the button and
select your Slack workspace.

## Deployment

If you want to deploy on your own Heroku instance, you need a working Heroku app with the Postgres addon. Add the
Slack environment variables (found in the Basic Information page of your app) to the Heroku config:

```
heroku config:set CLIENT_ID=XXXXXXXXX
heroku config:set CLIENT_SECRET=XXXXXXXXX
heroku config:set VERIFICATION_TOKEN=XXXXXXXXX
```

The DATABASE_URL variable should have been set and added when attaching the Postgres addon.

## TODO

+ rework as a package,
+ refactor SQL code in a module,
+ improve the templates,
+ deploy readthedocs


