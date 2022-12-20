FROM python:3.10

COPY requirements.txt /tmp
COPY *.py README.md /app/
WORKDIR /app
RUN pip install -r /tmp/requirements.txt

CMD [ "/usr/local/bin/streamlit", "run", "streamlit-app.py" ]