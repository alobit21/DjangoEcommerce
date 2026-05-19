======================================production===============================

git pull
python manage.py flush
python manage.py loaddata data.json
./deploy.sh



==============================locally==========================================

1. Database Export Execution


python3 manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e sessions -e admin.LogEntry --indent 4 -o data.json


2. Committed Locally
git add data.json
git commit -m "Refactored menu_cart layout aesthetics & exported clean database data.json fixture with natural keys"


🎯 Next Steps for Deployment
## Since my terminal session does not have access to your secure GitHub authentication credentials, please run git push directly in your terminal to publish the latest commit:

git push



=======================additionally===============================

# 1. Reset/Empty the local database
python3 manage.py flush

# 2. Reload the newly generated data.json fixture
python3 manage.py loaddata data.json

# 3. Start your local development server to inspect the shop catalog
python3 manage.py runserver
