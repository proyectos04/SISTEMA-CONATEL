import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.enableCors({
    origin: 'http://172.16.10.209:3000/',
  });
  await app.listen(process.env.PORT ?? 5000);
}
bootstrap();
