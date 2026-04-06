FROM node:22-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package files and install all dependencies
COPY package*.json ./
RUN npm install

# Copy your source code into the container
COPY . .

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

ARG VITE_API_INTERNAL_URL
ENV VITE_API_INTERNAL_URL=$VITE_API_INTERNAL_URL

# Build the Vue app (creates the /dist folder)
RUN npm run build

# Install the lightweight static file server
RUN npm install -g serve

# Expose the port the app will run on
EXPOSE 3000

# Start the server, pointing it to the newly created dist folder
CMD ["serve", "-s", "dist", "-l", "3000"]