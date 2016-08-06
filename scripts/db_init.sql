create user potholeuser with password 'mypass';
create database potholedb;
\c potholedb;
create extension postgis;
grant all privileges on database potholedb to potholeuser;
alter user potholeuser with superuser;
