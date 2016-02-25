deploy:
	[ -f "secrets.py" ] || ( echo "Please create a secrets.py file with:\n\thipchat_alertlib_token\n\thostedgraphite_api_key\n\tslack_alertlib_webhook_url\nfrom webapp's secrets.py." ; exit 1 )
	gcloud preview app deploy app.yaml module-listener.yaml --project khan-testimonials

test:
	python -m unittest testimonials_test

.PHONY: deploy
