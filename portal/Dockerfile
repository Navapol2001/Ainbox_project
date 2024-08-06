FROM node:21

WORKDIR /app

# Copy package.json and yarn.lock
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy the rest of your code
COPY . .

# Load environment variables from .env file
ENV $(cat .env | xargs)

# Build the application
RUN yarn build

# Expose the port the app runs on
EXPOSE 3001

# Start the application
CMD ["yarn", "start"]