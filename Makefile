deps:
	pip3 install -t lib -r requirements.txt

serve: deps
	env PYTHONPATH=lib python3 -m gunicorn -w 2 -b [::]:8080 --timeout 60 main:app --log-level debug

test: deps
	env PYTHONPATH=lib python3 -m unittest testimonials_test

# NOTE: we don't need to set PYTHONPATH here; it's done in appengine_config.py.
deploy: secrets.py
	gcloud app deploy app.yaml --project khan-testimonials-turtle --promote

# To create secrets.py.
secrets.py:
	echo "slack_alertlib_api_token = '`gcloud --project khan-academy secrets versions access latest --secret Slack__API_token_for_alertlib`'" > "$@"
	echo "slack_testimonials_turtle_api_token = '`gcloud --project khan-academy secrets versions access latest --secret Slack__API_token_for_Testimonials_Turtle`'" >> "$@"
	echo "slack_testimonials_search_api_token = '`gcloud --project khan-academy secrets versions access latest --secret Slack_API_token__for_search__for_Testimonials_Turtle`'" >> "$@"
	echo "slack_testimonials_slash_command_token = '`gcloud --project khan-academy secrets versions access latest --secret Slack__API_token__for_slash_commands__for_Testimonials_Turtle`'" >> "$@"
	echo "user_story_upvoting_secret = '`gcloud --project khan-academy secrets versions access latest --secret User_Story_Upvoting_Secret`'" >> "$@"

.PHONY: deploy serve test deps
