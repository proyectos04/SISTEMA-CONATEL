import { Controller, Get, Param, Req, Res } from '@nestjs/common';
import { ReadFileService } from './read-file.service';
import { Response, Request } from 'express';
@Controller('read-file')
export class ReadFileController {
  constructor(private readonly readServiceFile: ReadFileService) {
    this.readServiceFile = readServiceFile;
  }
  @Get(':folderId')
  async findFile(@Param('folderId') folderId: string) {
    return await this.readServiceFile.findFile(folderId);
  }
  @Get('profile/:folderId')
  async findProfile(@Param('folderId') folderId: string) {
    return await this.readServiceFile.findProfile(folderId);
  }
  @Get(':folderId/recipes')
  async findRecipes(@Param('folderId') folderId: string) {
    return await this.readServiceFile.findFiles(folderId);
  }
  @Get(':folderId/recipes/:fileName')
  async streamFile(
    @Param('folderId') folderId: string,
    @Param('fileName') fileName: string,
  ) {
    return await this.readServiceFile.streamFile(folderId, fileName);
  }
  @Get(':folderId/delivery')
  async findDeliverys(@Param('folderId') folderId: string) {
    return await this.readServiceFile.findFilesDelivery(folderId);
  }
  @Get(':folderId/delivery/:fileName')
  async streamFileDelivery(
    @Param('folderId') folderId: string,
    @Param('fileName') fileName: string,
  ) {
    return await this.readServiceFile.streamFileDelivery(folderId, fileName);
  }
  @Get(':folderId/recipes/date/:date')
  async getFilesByDateRecipes(
    @Param('folderId') folderId: string,
    @Param('date') date: string,
  ) {
    return await this.readServiceFile.getFilesByDateRecipes(folderId, date);
  }
  @Get(':folderId/delivery/date/:date')
  async getFilesByDateDelivery(
    @Param('folderId') folderId: string,
    @Param('date') date: string,
  ) {
    return await this.readServiceFile.getFilesByDateDelivery(folderId, date);
  }

  // Farmacia
  @Get(':folderId/recipes-farmacia')
  async findRecipesFarmacia(@Param('folderId') folderId: string) {
    return await this.readServiceFile.findRecipesFarmacia(folderId);
  }
  @Get(':folderId/recipes-farmacia/:fileName')
  async streamFileFarmacia(
    @Param('folderId') folderId: string,
    @Param('fileName') fileName: string,
  ) {
    return await this.readServiceFile.streamFileFarmacia(folderId, fileName);
  }
  @Get(':folderId/delivery-farmacia')
  async findDeliverysFarmacia(@Param('folderId') folderId: string) {
    return await this.readServiceFile.findDeliverysFarmacia(folderId);
  }
  @Get(':folderId/delivery-farmacia/:fileName')
  async streamFileDeliveryFarmacia(
    @Param('folderId') folderId: string,
    @Param('fileName') fileName: string,
  ) {
    return await this.readServiceFile.streamFileDeliveryFarmacia(
      folderId,
      fileName,
    );
  }
  @Get(':folderId/recipes-farmacia/date/:date')
  async getFilesByDateRecipesFarmacia(
    @Param('folderId') folderId: string,
    @Param('date') date: string,
  ) {
    return await this.readServiceFile.getFilesByDateRecipesFarmacia(
      folderId,
      date,
    );
  }
  @Get(':folderId/delivery-farmacia/date/:date')
  async getFilesByDateDeliveryFarmacia(
    @Param('folderId') folderId: string,
    @Param('date') date: string,
  ) {
    return await this.readServiceFile.getFilesByDateDeliveryFarmacia(
      folderId,
      date,
    );
  }
}
