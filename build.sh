set -o errexit

# Download wkhtmltopdf (precompiled binary) and install without needing superuser privileges
curl -L https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6/wkhtmltox_0.12.6-1.bionic_amd64.deb -o wkhtmltopdf.deb
# Use dpkg to install without superuser privileges
dpkg -i wkhtmltopdf.deb || true  # Ignore dpkg errors

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate