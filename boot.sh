source /opt/envs/klamu/bin/activate
# flask run &
exec gunicorn -b :8005 --access-logfile - --error-logfile - fromflask:app &
