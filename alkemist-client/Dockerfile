# Alkemist Frontend - Next.js 15
# Build: docker build -t alkemist-client:latest .
# Run: docker run -p 3000:3000 alkemist-client:latest

FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit

# Copy application code
COPY . .

# Build Next.js app
RUN npm run build

# Production image
FROM node:22-alpine

WORKDIR /app

# Install dumb-init to handle signals properly
RUN apk add --no-cache dumb-init

# Copy built app from builder
COPY --from=builder /app/package.json ./
COPY --from=builder /app/package-lock.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Install production dependencies only
RUN npm ci --prefer-offline --no-audit --omit=dev

# Environment
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Expose port
EXPOSE 3000

# Use dumb-init as entrypoint to handle signals
ENTRYPOINT ["dumb-init", "--"]

# Run Next.js server
CMD ["npm", "start"]
