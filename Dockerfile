FROM python:3.10

WORKDIR /code

COPY requirements.txt /code/requirements.txt

# RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --upgrade -r /code/requirements.txt

COPY ./app /code/app

EXPOSE 8200 

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--forwarded-allow-ips=\"*\"", "--host", "0.0.0.0", "--port", "8200"]