FROM python:3.12-alpine

RUN adduser -D sandbox
USER sandbox

WORKDIR /sandbox

COPY runner.py /sandbox/runner.py

#CMD ["python", "-u", "runner.py"]
ENTRYPOINT ["python", "-u", "runner.py"]
