# Install dependencies only when needed
FROM node:16-alpine AS deps

# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat

COPY ./Website/package.json /app/Website/package.json
COPY ./Website/yarn.lock /app/Website/yarn.lock
WORKDIR /app/Website
RUN yarn install --frozen-lockfile

# Rebuild the source code only when needed
FROM node:16-alpine AS builder

# copy the settings
COPY ./settings.toml /app/Website/settings.toml

# copy the logo
COPY ./logo.png /app/Website/public/images/logo.png
COPY ./logo_small.png /app/Website/public/images/logo_small.png

# copy the command docs
COPY ./ElevatorBot/docs /app/Website/data/docs

# copy everything else
COPY ./Website /app/Website
WORKDIR /app/Website
COPY --from=deps /app/Website/node_modules ./node_modules

RUN yarn build && yarn install --production --ignore-scripts --prefer-offline

# Production image, copy all the files and run next
FROM node:16-alpine AS runner
WORKDIR /app/Website

ENV NODE_ENV production

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

COPY --from=builder /app/Website/next.config.js ./
COPY --from=builder /app/Website/settings.toml ./settings.toml
COPY --from=builder /app/Website/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/Website/.next ./.next
COPY --from=builder /app/Website/node_modules ./node_modules
COPY --from=builder /app/Website/package.json ./package.json

USER nextjs

ENV PORT 3000
ENV NEXT_TELEMETRY_DISABLED 1

CMD ["node_modules/.bin/next", "start"]
EXPOSE 3000
