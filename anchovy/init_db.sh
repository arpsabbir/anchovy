#!/bin/bash

SETTINGS=${DJANGO_SETTINGS_MODULE}
# masterdata load で使うセッティング名
if [ $# -eq 1 ]; then
    if [ "${1:0:11}" == "--settings=" ]; then
        SETTINGS=${1#--settings=}
    fi
fi

if [ ! "${SETTINGS}" ]; then
    #echo "実行するには --settings= オプションを指定してください" 1>&2
    #exit 1
    SETTINGS='settings.settings'
fi

echo "settings=${SETTINGS}"

if [ "${SETTINGS/production}" != "${SETTINGS}" ] ; then
    echo "本番環境では実行できません" 1>&2
    exit 1
fi

# clean pyc file
python manage.py clean_pyc --settings=${SETTINGS}

echo "DBの完全初期化を行います。※注意!保存されているデータは全て消去されます"

read -p "Database Master User ?> " DB_USER
read -s -p "Database Master Password ?> " DB_PASSWORD

echo

# recreate db
DATABASE_NAMES=`python -c "import django.template.loader; django.template.loader.add_to_builtins = lambda x:x;from sets import Set;from ${SETTINGS} import DATABASES;print ' '.join(list(Set([db for db in DATABASES.keys()])))"`
for DATABASE_NAME in ${DATABASE_NAMES}
do
    DB_NAME=`python -c "import django.template.loader; django.template.loader.add_to_builtins = lambda x:x;from ${SETTINGS} import DATABASES;print DATABASES['${DATABASE_NAME}']['NAME']"`
    DB_HOST=`python -c "import django.template.loader; django.template.loader.add_to_builtins = lambda x:x;from ${SETTINGS} import DATABASES;print DATABASES['${DATABASE_NAME}']['HOST'] if DATABASES['default']['HOST'] else 'localhost'"`
    DB_PORT=`python -c "import django.template.loader; django.template.loader.add_to_builtins = lambda x:x;from ${SETTINGS} import DATABASES;print DATABASES['${DATABASE_NAME}']['PORT'] if DATABASES['default']['PORT'] else 3306"`

    if [ "${DB_HOST:0:1}" == "/" ]; then
        DB_HOST_OPTION="--socket=${DB_HOST}"
    else
        DB_HOST_OPTION="--host=${DB_HOST}"
    fi

    R=`echo "SELECT 1 " | mysql --user=${DB_USER} --password=${DB_PASSWORD} ${DB_HOST_OPTION} --port=${DB_PORT}`
    if [ ! "${R}" ]; then
        exit 1
    fi

    echo "recreate '${DATABASE_NAME}' database = ${DB_NAME} ${DB_HOST}:${DB_PORT}"
    echo "DROP DATABASE IF EXISTS \`${DB_NAME}\`;CREATE DATABASE \`${DB_NAME}\` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;" | mysql --user=${DB_USER} --password=${DB_PASSWORD} ${DB_HOST_OPTION} --port=${DB_PORT}
done

# DB初期化 (syncdb, migrate)
python manage.py init_db --settings=${SETTINGS}
# adminユーザ登録
echo "Creating user: admin/admin"
#python manage.py createsuperuser --email=admin@example.com --username=admin --settings=${SETTINGS}
# ユーザーID: admin パスワード admin を自動作成する
python manage.py createadminuser --settings=${SETTINGS}
