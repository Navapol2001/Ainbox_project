FROM node:21

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn

COPY . /app

# Load environment variables from .env file
ENV $(cat .env | xargs)

EXPOSE 3002

CMD ["yarn", "dev"]