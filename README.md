# Pothole Reporting Android app's server implementation in Django
## Documentation for [ SafeStreet-Server ](http://safestreet-server.readthedocs.io/en/latest/)

## Installation
1. Install postgresql (`sudo apt-get install postgresql postgresql-contrib`)
2. Install postgis (`sudo apt-get install postgresql-9.5-postgis-2.1`)
3. follow the instructions in the [link]( http://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS22UbuntuPGSQL95Apt ) to install postgresql-9.5-postgis-2.2  
4. if you are running postgres9.3 and want to upgrade to postgres9.5 below are the steps to do it. [upgrade-postgres-9.3-to-9.5.md](https://gist.github.com/johanndt/6436bfad28c86b28f794)
```
sudo pg_dropcluster 9.5 main --stop
sudo pg_upgradecluster 9.3 main
sudo pg_dropcluster 9.3 main
```
4. Create user 'potholeuser' with password 'mypass' in psql, create database 'potholedb' with postgis extension in it, grant superuser permission to 'potholeuser'
commands to be executed in order
   1. `sudo -i -u postgres`
   2. `psql`
   3. `create user potholeuser with password 'mypass'`
   4. `create database potholedb;`
   5. `\c potholedb;`
   6. `create extension postgis;`
   7. `grant all privileges on database potholedb to potholeuser;`
   8. `alter user potholeuser with superuser;`
4. Install libpq-dev and python dev (`sudo apt-get install libpq-dev python-dev`)
5. Install pip
6. Install virtualenv (`pip install virtualenv`)
7. Create the virtual environment and activate it
8. Install requirements using pip (`pip install -r requirements.txt`)
If Pillow doesn't build then, `sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk`
9. (local) Use pip to install `isort`, `pep8` and `pylint` for development
10. (optional) Install spatialite for quickly running automated tests while writing tests(Will also have to update settings) (`sudo apt-get install libsqlite3-mod-spatialite`)
11. Run tests in directory (`coverage run --source '.' manage.py test`)
12. Create super user (`python manage.py createsuperuser`)
13. Run server (`python manage.py runserver`)
