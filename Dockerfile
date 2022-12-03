FROM python:3.10-alpine

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN apk add git \
 && pip install pipenv \
 && pipenv install --deploy --system \
 && pip uninstall pipenv -y \
 && apk del git

COPY . .

ENTRYPOINT ["python", "-m", "tado_switchbot_temperature"]
CMD ["sync"]
