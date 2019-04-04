FROM cybercom/api
MAINTAINER Mark Stacy <markstacy@ou.edu>
ADD . /usr/src/app
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["gunicorn", "--config=gunicorn.py", "api.wsgi:application"]
