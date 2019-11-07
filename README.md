# slack-testimonials-bot
Slack bot that shares and promotes awareness of KA's testimonials

To run locally:
* First run `make decrypt_secrets`, then follow the instructions
* Then run `make deps`
* Then run `make serve`

== Deployment

There's two separate things to deploy here:

The api endpoints that send new testimonials to slack runs as a appengine
standard application. Deploy these by running `make deploy`. To test that the
deploy succeeded, you can hit `/test_new_testimonial` and verify that a new
default testimonial is sent to the `#testimonials` channel.

The slack client that listens for reactions to slack messages and updates vote
totals (`listener.py`) runs on toby, using the configuration found
[here](https://github.com/Khan/aws-config/blob/master/toby/etc/systemd/system/slack-testimonials-bot.service).
To update that code, follow these steps:

```
# SSH into toby:
gcloud --project=khan-internal-services compute ssh \
    ubuntu@toby-internal-webserver

# cd to the project directory
cd /home/ubuntu/slack-testimonials-bot

# pull the latest code
git fetch && git checkout origin/master

# restart the service to pull in that latest code
sudo systemctl restart slack-testimonials-bot
```

To test that this deploy succeeded, upvote a recently high quality testimonial.
This should eventually reshare that testimonial to the `#khan-academy` channel.
