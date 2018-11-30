deploy:
	[ -f "secrets.py" ] || ( echo "Please create a secrets.py file with:\n\thipchat_alertlib_token\n\thostedgraphite_api_key\n\tslack_alertlib_webhook_url\nfrom webapp's secrets.py." ; exit 1 )
	appcfg.py update -A khan-testimonials-turtle .

serve:
	dev_appserver.py --port=8081 .

test:
	python -m unittest testimonials_test

# to create secrets.py
secrets.py secrets_decrypt decrypt_secrets:
	@if [ -s "secrets.py" ]; then \
		sed -n 's/secrets_secret = "\(.*\)"/\1/p' secrets.py | openssl cast5-cbc -md md5 -d -in secrets.py.cast5 -out secrets.py -pass stdin && \
		echo "Automatically retrieved password from secrets.py" && \
		echo "secrets.py has been successfully created! You're done."; \
	else \
		echo "Get the password from here:"; \
		echo "https://phabricator.khanacademy.org/K133"; \
		openssl cast5-cbc -md md5 -d -in secrets.py.cast5 -out secrets.py; \
	fi
	@chmod 600 secrets.py

# for updating secrets.py
secrets.py.cast5 secrets_encrypt encrypt_secrets:
	sed -n 's/secrets_secret = "\(.*\)"/\1/p' secrets.py | openssl cast5-cbc -md md5 -e -in secrets.py -out secrets.py.cast5 -pass stdin && \
	echo "secrets.py.cast5 has been successfully created! You're done.";

.PHONY: deploy
