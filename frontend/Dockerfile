FROM node:14 AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install --force

COPY . .

RUN npm run build

FROM node:14

RUN npm install -g serve

COPY --from=builder /app/build /app/build

WORKDIR /app

CMD ["serve", "-s", "build"]