set -o errexit


apt-get update

apt-get install -y wkhtmltopdf

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate