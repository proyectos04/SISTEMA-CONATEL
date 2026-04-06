import { HttpException, HttpStatus, Injectable } from '@nestjs/common';
import * as fsPromise from 'fs/promises';
import * as fs from 'fs';
import path, { join } from 'path';
@Injectable()
export class FileSaveService {
  async saveOneFile(file: Express.Multer.File, folderId: string) {
    try {
      const folderOriginTemp = join(__dirname, '..', '..', 'uploads', 'temp');
      const dest = join(__dirname, '..', '..', 'uploads', folderId);
      const destFinal = join(dest, file.originalname);
      await fsPromise.mkdir(dest, { recursive: true });
      await fsPromise.rename(
        join(folderOriginTemp, file.originalname),
        destFinal,
      );
    } catch (error) {
      throw new HttpException(
        'Error Al Mover El Archivo',
        HttpStatus.AMBIGUOUS,
      );
    }
    return { message: 'Archivo Guardado', status: HttpStatus.OK };
  }

  async saveProfile(file: Express.Multer.File, folderId: string) {
    try {
      const folderOriginTemp = join(__dirname, '..', '..', 'uploads', 'temp');
      const dest = join(__dirname, '..', '..', 'uploads', folderId, 'profile');
      const destFinal = join(dest, file.originalname);
      await fsPromise.mkdir(dest, { recursive: true });
      await fsPromise.rename(
        join(folderOriginTemp, file.originalname),
        destFinal,
      );
    } catch (error) {
      throw new HttpException(
        'Error Al Mover El Archivo',
        HttpStatus.AMBIGUOUS,
      );
    }
    return { message: 'Archivo Guardado', status: HttpStatus.OK };
  }

  async saveArrayFiles(recipe: Array<Express.Multer.File>, folderId: string) {
    const folderOriginTempArray = join(
      __dirname,
      '..',
      '..',
      'uploads',
      'temp',
      'arrayFiles',
    );

    const destFinal = join(__dirname, '..', '..', 'uploads', folderId);
    const destFinalRecipe = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'recipes_oac',
    );
    if (fs.existsSync(destFinal)) {
      await fsPromise.mkdir(destFinalRecipe, { recursive: true });
    } else if (!fs.existsSync(destFinal)) {
      await fsPromise.mkdir(destFinal, { recursive: true });
      await fsPromise.mkdir(destFinalRecipe, { recursive: true });
    } else {
      throw new HttpException('No Existe La Carpeta', HttpStatus.CONFLICT);
    }

    try {
      for (let index = 0; index < recipe.length; index++) {
        const originFiles = join(
          folderOriginTempArray,
          recipe[index].originalname,
        );
        await fsPromise.rename(
          originFiles,
          join(destFinalRecipe, recipe[index].originalname),
        );
      }
    } catch (error) {
      throw new HttpException(
        'Error Al Mover El Archivo',
        HttpStatus.AMBIGUOUS,
      );
    }
    return {
      message: 'Archivo Guardado',
      resource: destFinalRecipe,
      status: HttpStatus.OK,
    };
  }

  async saveArrayFilesDelivery(
    Delivery: Array<Express.Multer.File>,
    folderId: string,
  ) {
    const folderOriginTempArray = join(
      __dirname,
      '..',
      '..',
      'uploads',
      'temp',
      'arrayFiles',
    );

    const destFinal = join(__dirname, '..', '..', 'uploads', folderId);
    const destFinalDelivery = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'deliverys_oac',
    );

    try {
      if (!fs.existsSync(destFinal)) {
        await fsPromise.mkdir(destFinal, { recursive: true });
        await fsPromise.mkdir(destFinalDelivery, { recursive: true });
      } else {
        await fsPromise.mkdir(destFinalDelivery, { recursive: true });
      }
    } catch {
      throw new HttpException('No Existe La Carpeta', HttpStatus.CONFLICT);
    }

    try {
      for (let index = 0; index < Delivery.length; index++) {
        const originFiles = join(
          folderOriginTempArray,
          Delivery[index].originalname,
        );
        await fsPromise.rename(
          originFiles,
          join(destFinalDelivery, Delivery[index].originalname),
        );
      }
    } catch (error) {
      throw new HttpException(
        'Error Al Mover El Archivo',
        HttpStatus.AMBIGUOUS,
      );
    }
    throw new HttpException('Archivo Guardado', HttpStatus.OK);
  }
  async saveArrayFilesMedical(
    recipe: Array<Express.Multer.File>,
    folderId: string,
  ) {
    const folderOriginTempArray = join(
      __dirname,
      '..',
      '..',
      'uploads',
      'temp',
      'arrayFiles',
    );

    const destFinal = join(__dirname, '..', '..', 'uploads', folderId);
    const destFinalRecipe = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'recipes_farmacia',
    );
    if (fs.existsSync(destFinal)) {
      await fsPromise.mkdir(destFinalRecipe, { recursive: true });
    } else if (!fs.existsSync(destFinal)) {
      await fsPromise.mkdir(destFinal, { recursive: true });
      await fsPromise.mkdir(destFinalRecipe, { recursive: true });
    } else {
      throw new HttpException('No Existe La Carpeta', HttpStatus.CONFLICT);
    }

    try {
      for (let index = 0; index < recipe.length; index++) {
        const originFiles = join(
          folderOriginTempArray,
          recipe[index].originalname,
        );
        await fsPromise.rename(
          originFiles,
          join(destFinalRecipe, recipe[index].originalname),
        );
      }
    } catch (error) {
      throw new HttpException(
        'Error Al Mover El Archivo',
        HttpStatus.AMBIGUOUS,
      );
    }
    return {
      status: HttpStatus.OK,
      message: 'Archivo Guardado',
      resource: destFinalRecipe,
    };
  }
  async saveArrayFileDeliveryMedical(
    Delivery: Array<Express.Multer.File>,
    folderId: string,
  ) {
    const folderOriginTempArray = join(
      __dirname,
      '..',
      '..',
      'uploads',
      'temp',
      'arrayFiles',
    );

    const destFinal = join(__dirname, '..', '..', 'uploads', folderId);
    const destFinalDelivery = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'deliverys_farmacia',
    );

    try {
      if (!fs.existsSync(destFinal)) {
        await fsPromise.mkdir(destFinal, { recursive: true });
        await fsPromise.mkdir(destFinalDelivery, { recursive: true });
      } else {
        await fsPromise.mkdir(destFinalDelivery, { recursive: true });
      }
    } catch {
      throw new HttpException('No Existe La Carpeta', HttpStatus.CONFLICT);
    }

    try {
      if (!fs.existsSync(destFinal)) {
        await fsPromise.mkdir(destFinal, { recursive: true });
        await fsPromise.mkdir(destFinalDelivery, { recursive: true });
      } else {
        await fsPromise.mkdir(destFinalDelivery, { recursive: true });
      }
    } catch {
      throw new HttpException('No Existe La Carpeta', HttpStatus.CONFLICT);
    }

    try {
      for (let index = 0; index < Delivery.length; index++) {
        const originFiles = join(
          folderOriginTempArray,
          Delivery[index].originalname,
        );
        await fsPromise.rename(
          originFiles,
          join(destFinalDelivery, Delivery[index].originalname),
        );
      }
    } catch (error) {
      throw new HttpException(
        'Error Al Mover El Archivo',
        HttpStatus.AMBIGUOUS,
      );
    }
    return {
      status: HttpStatus.OK,
      message: 'Archivo Guardado',
      resource: destFinalDelivery,
    };
  }
}
