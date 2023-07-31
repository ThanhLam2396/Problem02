FROM python:3.9 as build
WORKDIR /code/app/
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .
FROM gcr.io/distroless/python3-debian11
COPY --from=build /code/app/ /code/app/
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
WORKDIR /code/app/

ENV PYTHONPATH=/usr/local/lib/python3.9/site-packages
EXPOSE 8000

CMD ["run.py"]