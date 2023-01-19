FROM python:3.9

COPY requirements.txt /tmp
COPY *.py README.md /app/
COPY img/* /app/img/

WORKDIR /app
RUN pip install -r /tmp/requirements.txt
RUN printf "\n\nBuild on $(date)\n" >> /app/README.md

CMD [ "/usr/local/bin/streamlit", "run", "streamlit-app.py" ]
