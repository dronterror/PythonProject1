FROM node:20-alpine AS build

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

# Install Node.js for testing capabilities
RUN apk add --no-cache nodejs npm

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html
COPY --from=build /app/package.json /app/package-lock.json /app/
COPY --from=build /app/node_modules /app/node_modules
COPY --from=build /app/src /app/src
COPY --from=build /app/vitest.config.js /app/
COPY nginx.conf /etc/nginx/conf.d/default.conf

WORKDIR /app

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 