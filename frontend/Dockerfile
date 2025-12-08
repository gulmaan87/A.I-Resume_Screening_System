FROM node:20-alpine AS base

WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Build arguments for environment variables (must be set at build time)
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Copy package files
COPY package.json package-lock.json* ./ 

# Install all dependencies (including devDependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build with environment variables baked in at build time
RUN npm run build

EXPOSE 4173

# Use Vite preview for serving the built application
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]

