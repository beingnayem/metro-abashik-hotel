set -o errexit


curl -L https://github.com/wkhtmltopdf/packaging/releases/download/v0.12.6/wkhtmltox_0.12.6-1.bionic_amd64.deb -o wkhtmltopdf.deb
dpkg -i wkhtmltopdf.deb
apt-get install -f  

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate