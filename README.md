# Pothole Reporting Android app's server implementation in Django
## Documentation for [ SafeStreet-Server ](http://safestreet-server.readthedocs.io/en/latest/)

## Installation
1. Install postgresql (`sudo apt-get install postgresql postgresql-contrib`)
2. Install postgis (`sudo apt-get install postgresql-9.5-postgis-2.1`)
3. if you want to install `postgresql-9.5-postgis-2.2` instead of version `2.1` follow the instructions in the [link]( http://trac.osgeo.org/postgis/wiki/UsersWikiPostGIS22UbuntuPGSQL95Apt ) to install postgresql-9.5-postgis-2.2  
4. if you are running postgres9.3 and want to upgrade to postgres9.5 below are the steps to do it. [upgrade-postgres-9.3-to-9.5.md](https://gist.github.com/johanndt/6436bfad28c86b28f794)
```bash
sudo pg_dropcluster 9.5 main --stop
sudo pg_upgradecluster 9.3 main
sudo pg_dropcluster 9.3 main
```
5. Create user 'potholeuser' with password 'mypass' in psql, create database 'potholedb' with postgis extension in it, grant superuser permission to 'potholeuser'
commands to be executed in order
   1. `sudo -i -u postgres`
   2. `psql`
   3. `create user potholeuser with password 'mypass'`
   4. `create database potholedb;`
   5. `\c potholedb;`
   6. `create extension postgis;`
   7. `grant all privileges on database potholedb to potholeuser;`
   8. `alter user potholeuser with superuser;`
6. Install libpq-dev and python dev (`sudo apt-get install libpq-dev python-dev`)
7. Install pip (pip is already installed if you're using Python 2 >=2.7.9 or Python 3 >=3.4 but you need to updage pip)
   - run `pip install pip --upgrade`
8. Install [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) `pip install virtualenv`
9. install [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html) `pip install virtualenvwrapper`
9. Create the virtual environment `mkvirtualenv pothole` and to configure it read the documentations and activate the `pothole` virtualenv  `workon pothole`
10. Install requirements using pip (`pip install -r requirements.txt`). You should be in root of the project before you run this command.
    If Pillow doesn't build then, `sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk`
11. (local) Use pip to install `isort`, `pep8` and `pylint` for development
12. (optional) Install spatialite for quickly running automated tests while writing tests(Will also have to update settings) (`sudo apt-get install libsqlite3-mod-spatialite`)
13. (optional) Run tests in directory (`coverage run --source '.' manage.py test`)
14. Create super user (`python manage.py createsuperuser`)
15. Run server (`python manage.py runserver`)
