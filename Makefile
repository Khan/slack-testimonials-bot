deploy:
	[ -f "secrets.py" ] || ( echo "Please create a secrets.py file with:\n\thipchat_alertlib_token\n\thostedgraphite_api_key\n\tslack_alertlib_webhook_url\nfrom webapp's secrets.py." ; exit 1 )
	appcfg.py update -A khan-testimonials-turtle .

serve:
	dev_appserver.py --port=8081 .

test:
	python -m unittest testimonials_test

.PHONY: deploy
