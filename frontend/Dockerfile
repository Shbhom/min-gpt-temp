FROM node:14 AS builder

WORKDIR /app

COPY package*.json ./

ARG API="http://localhost:8080"
ARG SECRET="JKDWJD!@132980"

# echo the build args
RUN echo ${API}
RUN echo ${SECRET}

RUN npm install --force

COPY . .

ENV REACT_APP_API=$API
ENV REACT_APP_SECRET=$SECRET

RUN npm run build

FROM node:14

RUN npm install -g serve

COPY --from=builder /app/build /app/build

WORKDIR /app

CMD ["serve", "-s", "build"]