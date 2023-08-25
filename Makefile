deploy:
	[ -f "secrets.py" ] || ( echo "Please create a secrets.py file by running 'make decrypt_secrets'." ; exit 1 )
	gcloud app deploy app.yaml --project khan-testimonials-turtle --version 1 --promote

serve:
	dev_appserver.py --admin_port=9000 --port=9081 .

test:
	python -m unittest testimonials_test

deps:
	pip install -t lib -r requirements.txt

# to create secrets.py
secrets.py secrets_decrypt decrypt_secrets:
	@if [ -s "secrets.py" ]; then \
		sed -n 's/secrets_secret = "\(.*\)"/\1/p' secrets.py | openssl cast5-cbc -md md5 -d -in secrets.py.cast5 -out secrets.py -pass stdin && \
		echo "Automatically retrieved password from secrets.py" && \
		echo "secrets.py has been successfully created! You're done."; \
	else \
		echo "Get the password from here:"; \
		echo "https://console.cloud.google.com/security/secret-manager/secret/slack_testimonials_bot_secrets_py_decrypt_password/versions?project=khan-academy"; \
		openssl cast5-cbc -md md5 -d -in secrets.py.cast5 -out secrets.py; \
	fi
	@chmod 600 secrets.py

# for updating secrets.py
secrets.py.cast5 secrets_encrypt encrypt_secrets:
	sed -n 's/secrets_secret = "\(.*\)"/\1/p' secrets.py | openssl cast5-cbc -md md5 -e -in secrets.py -out secrets.py.cast5 -pass stdin && \
	echo "secrets.py.cast5 has been successfully created! You're done.";

.PHONY: deploy
