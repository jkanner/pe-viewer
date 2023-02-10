FROM python:3.9

COPY requirements.txt /tmp
RUN apt-get update && apt-get full-upgrade -y
RUN pip install -r /tmp/requirements.txt

# create unprivileged user, make /app their home directory for simplicity sake
RUN  useradd -s /usr/sbin/nologin -m -d /app peviewer
# finish the install as peviewer, in their $HOME
USER peviewer
WORKDIR /app
RUN mkdir -p .streamlit/cache/
COPY --chown=peviewer *.py README.md /app/
COPY --chown=peviewer img/* /app/img/

# uncomment these to brand the timestamp of the build in the back-hole-ellipse image
#COPY docker/brand-image.py /tmp
#RUN python3 /tmp/brand-image.py
RUN printf "\n\nBuild on $(date)\n" >> /app/README.md

EXPOSE 8501


CMD [ "/usr/local/bin/streamlit", "run", "streamlit-app.py" ]
