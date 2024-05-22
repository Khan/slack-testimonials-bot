deps:
	pip3 install -t lib -r requirements.txt

serve: deps
	python3 -m gunicorn -w 2 -b [::]:8080 --timeout 60 main:app --log-level debug

test:
	python3 -m unittest testimonials_test

deploy: secrets.py
	gcloud app deploy app.yaml --project khan-testimonials-turtle --promote

# to create secrets.py
secrets.py:
	echo "slack_alertlib_webhook_url = '`gcloud --project khan-academy secrets versions access latest --secret Slack__webhook_url_for_alertlib`'" > "$@"
	echo "slack_testimonials_turtle_api_token = '`gcloud --project khan-academy secrets versions access latest --secret Slack__API_token_for_Testimonials_Turtle`'" >> "$@"
	echo "slack_testimonials_search_api_token = '`gcloud --project khan-academy secrets versions access latest --secret Slack_API_token__for_search__for_Testimonials_Turtle`'" >> "$@"
	echo "slack_testimonials_slash_command_token = '`gcloud --project khan-academy secrets versions access latest --secret Slack__API_token__for_slash_commands__for_Testimonials_Turtle`'" >> "$@"

.PHONY: deploy serve test deps
