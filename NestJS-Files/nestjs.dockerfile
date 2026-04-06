FROM node
WORKDIR /app/NestFS
COPY package.json .
RUN npm install -g pnpm
RUN pnpm i
COPY . .
EXPOSE 4000

CMD [ "pnpm start"]