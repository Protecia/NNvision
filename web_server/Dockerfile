FROM nnvision_server_base

WORKDIR /NNvision
COPY . /NNvision

# Make django a git repo
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y git
RUN rm -rf ./django && git clone https://updateProtecia:proteciaforupdate@github.com/Protecia/django.git


# Activate postgresql
USER postgres
RUN    /etc/init.d/postgresql start &&\
       psql --command "CREATE USER djdb WITH PASSWORD 'protecia';" && \
       psql --command "CREATE DATABASE protecia WITH OWNER djdb;" && /etc/init.d/postgresql stop

USER root
# Activate django
RUN cd django && mv projet/settings.base.py projet/settings.py && python3 manage.py collectstatic && /etc/init.d/postgresql start &&\
    python3 manage.py makemigrations &&  python3 manage.py migrate && python3 manage.py loaddata group.json &&\
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@protecia.com', 'protecia')" | python3 manage.py shell && \
    /etc/init.d/postgresql stop && mv projet/settings.py projet/settings.base.py

RUN django/change_right.sh  && a2enmod ssl && a2enmod rewrite && a2dissite 000-default && a2ensite protecia-ssl && a2ensite protecia-80 && rm Dockerfile* && rm build.sh
 

CMD ["/NNvision/start.sh"]
