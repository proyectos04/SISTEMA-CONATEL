import {
  Controller,
  HttpException,
  HttpStatus,
  Param,
  Post,
  UploadedFiles,
  UseInterceptors,
} from '@nestjs/common';
import * as fsPromise from 'fs/promises';
import { FileInterceptor, FilesInterceptor } from '@nestjs/platform-express';
import { UploadedFile } from '@nestjs/common';
import { FileSaveService } from './file-save.service';
import { FileValidationPipePipe } from './file-validation-pipe/file-validation-pipe.pipe';
import { diskStorage } from 'multer';
import { join } from 'path';

@Controller('file-save')
export class FileSaveController {
  constructor(private readonly fileSaveService: FileSaveService) {
    this.fileSaveService = fileSaveService;
  }
  @Post('/upload/:folderId')
  @UseInterceptors(
    FileInterceptor('file', {
      storage: diskStorage({
        destination: `./uploads/temp`,
        filename: (req, file, cb) => {
          cb(null, file.originalname);
        },
      }),
    }),
  )
  async saveOneFile(
    @UploadedFile(new FileValidationPipePipe()) file: Express.Multer.File,
    @Param('folderId') folderId: string,
  ) {
    return this.fileSaveService.saveOneFile(file, folderId);
  }
  @Post('/upload/profile/:folderId')
  @UseInterceptors(
    FileInterceptor('file', {
      storage: diskStorage({
        destination: `./uploads/temp`,
        filename: (req, file, cb) => {
          cb(null, file.originalname);
        },
      }),
    }),
  )
  async saveProfile(
    @Param('folderId') folderId: string,
    @UploadedFile(new FileValidationPipePipe()) file: Express.Multer.File,
  ) {
    return this.fileSaveService.saveProfile(file, folderId);
  }

  @Post('/upload/:folderId/recipe/delivery')
  @UseInterceptors(
    FilesInterceptor('delivery', 1, {
      storage: diskStorage({
        destination: `./uploads/temp/arrayFiles`,
        filename: (req, file, cb) => {
          cb(null, file.originalname);
        },
      }),
    }),
  )
  async saveArrayFileDelivery(
    @UploadedFiles(new FileValidationPipePipe())
    delivery: Array<Express.Multer.File>,
    @Param('folderId') folderId: string,
  ) {
    return this.fileSaveService.saveArrayFilesDelivery(delivery, folderId);
  }

  @Post('/upload/:folderId/recipe-medical')
  @UseInterceptors(
    FilesInterceptor('recipe', 5, {
      storage: diskStorage({
        destination: `./uploads/temp/arrayFiles`,
        filename: (req, file, cb) => {
          cb(null, file.originalname);
        },
      }),
    }),
  )
  async saveArrayFileMedical(
    @UploadedFiles(new FileValidationPipePipe())
    recipe: Array<Express.Multer.File>,
    @Param('folderId') folderId: string,
  ) {
    return this.fileSaveService.saveArrayFilesMedical(recipe, folderId);
  }

  @Post('/upload/:folderId/recipe/delivery-medical')
  @UseInterceptors(
    FilesInterceptor('delivery', 1, {
      storage: diskStorage({
        destination: `./uploads/temp/arrayFiles`,
        filename: (req, file, cb) => {
          cb(null, file.originalname);
        },
      }),
    }),
  )
  async saveArrayFileDeliveryMedical(
    @UploadedFiles(new FileValidationPipePipe())
    delivery: Array<Express.Multer.File>,
    @Param('folderId') folderId: string,
  ) {
    return this.fileSaveService.saveArrayFileDeliveryMedical(
      delivery,
      folderId,
    );
  }
}
