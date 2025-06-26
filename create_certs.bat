@echo off
docker run --rm -v "%cd%/certs:/certs" alpine/openssl req -x509 -newkey rsa:2048 -keyout /certs/medlog.local.key -out /certs/medlog.local.crt -days 365 -nodes -subj "/C=US/ST=CA/L=Local/O=MedLog/CN=*.medlog.local"
echo Certificates created successfully! 