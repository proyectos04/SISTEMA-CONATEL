import {
  HttpException,
  HttpStatus,
  Injectable,
  NotFoundException,
  StreamableFile,
} from '@nestjs/common';
import path, { extname, join } from 'path';
import * as fs from 'fs';
import * as fsPromise from 'fs/promises';
import { Response } from 'express';

@Injectable()
export class ReadFileService {
  async findFile(folderId: string) {
    const MIMETYPES = {
      '.pdf': 'application/pdf',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
    };
    const originFiles = join(__dirname, '..', '..', 'uploads', folderId);
    const listFile = await fsPromise.readdir(join(originFiles));
    console.log(listFile);
    const findile = listFile.find(
      (file) =>
        file.endsWith('pdf') ||
        file.endsWith('png') ||
        file.endsWith('jpg') ||
        file.endsWith('jpeg'),
    );
    if (findile != undefined) {
      const directionFile = join(originFiles, findile);
      const file = fs.createReadStream(directionFile);
      const mimetype = MIMETYPES[extname(directionFile)];
      return new StreamableFile(file, {
        type: mimetype,
        disposition: 'inline',
      });
    } else {
      throw new NotFoundException('Archivo no encontrado');
    }
  }
  async findProfile(folderId: string) {
    const MIMETYPES = {
      '.pdf': 'application/pdf',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
    };

    try {
      // Usar path absoluto o relativo correctamente
      const uploadsBase = process.cwd(); // Directorio actual del proceso
      const originFiles = join(uploadsBase, 'uploads', folderId, 'profile');

      console.log('Buscando en ruta:', originFiles);

      // Verificar si el directorio existe
      try {
        await fsPromise.access(originFiles);
      } catch (accessError) {
        console.error('Directorio no accesible:', originFiles);
        throw new NotFoundException('Directorio de perfil no encontrado');
      }

      // Listar archivos
      const listFile = await fsPromise.readdir(originFiles);
      console.log('Archivos encontrados:', listFile);

      const findile = listFile.find(
        (file) =>
          file.endsWith('.png') ||
          file.endsWith('.jpg') ||
          file.endsWith('.jpeg') ||
          file.toLowerCase().endsWith('.png') ||
          file.toLowerCase().endsWith('.jpg') ||
          file.toLowerCase().endsWith('.jpeg'),
      );

      if (findile) {
        const directionFile = join(originFiles, findile);
        console.log('Archivo seleccionado:', directionFile);

        // Verificar que el archivo existe
        await fsPromise.access(directionFile);

        const file = fs.createReadStream(directionFile);
        const mimetype =
          MIMETYPES[extname(directionFile).toLowerCase()] ||
          'application/octet-stream';

        return new StreamableFile(file, {
          type: mimetype,
          disposition: 'inline',
        });
      } else {
        console.log('No se encontraron archivos de imagen en:', listFile);
        throw new NotFoundException('Archivo de imagen no encontrado');
      }
    } catch (error) {
      console.error('Error en findProfile:', error);

      if (error instanceof NotFoundException) {
        throw error;
      }

      throw new NotFoundException('Error al buscar el archivo de perfil');
    }
  }
  async findFiles(folderId: string) {
    const folderOriginRecipes = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'recipes_oac',
    );
    try {
      const listRecipes = await fsPromise.readdir(folderOriginRecipes);
      const filesInfo = await Promise.all(
        listRecipes.map(async (file) => {
          const filePath = join(folderOriginRecipes, file);
          const stats = await fsPromise.stat(filePath);
          return {
            name: file,
            size: stats.size,
            createdAt: stats.mtime,
            updatedAt: stats.mtime,
            direcction: stats.nlink,
          };
        }),
      );
      return {
        success: true,
        files: filesInfo,
      };
    } catch {
      throw new NotFoundException('No se encontró la carpeta de recetas');
    }
  }

  async streamFile(folderId: string, fileName: string) {
    const MIMETYPES = {
      '.pdf': 'application/pdf',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
    };
    const originFiles = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'recipes_oac',
    );
    const listFile = await fsPromise.readdir(join(originFiles));
    console.log(listFile);
    const pdf = listFile.find((file) => file === fileName.toString());
    if (pdf != undefined) {
      const directionFile = join(originFiles, pdf);
      const file = fs.createReadStream(directionFile);
      const mimetype = MIMETYPES[extname(directionFile)];
      return new StreamableFile(file, {
        type: mimetype,
        disposition: 'inline',
      });
    } else {
      throw new NotFoundException('Archivo no encontrado');
    }
  }
  async findFilesDelivery(folderId: string) {
    const folderOriginDelivery = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'deliverys_oac',
    );
    try {
      const listDelivery = await fsPromise.readdir(folderOriginDelivery);
      console.log(folderOriginDelivery);
      const filesInfo = await Promise.all(
        listDelivery.map(async (file) => {
          const filePath = join(folderOriginDelivery, file);
          const stats = await fsPromise.stat(filePath);
          return {
            name: file,
            size: stats.size,
            createdAt: stats.mtime,
            updatedAt: stats.mtime,
          };
        }),
      );
      return {
        success: true,
        files: filesInfo,
      };
    } catch {
      throw new NotFoundException('No se encontró la carpeta de Entregas');
    }
  }
  async streamFileDelivery(folderId: string, fileName: string) {
    const MIMETYPES = {
      '.pdf': 'application/pdf',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
    };
    const originFiles = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'deliverys_oac',
    );
    const listFile = await fsPromise.readdir(join(originFiles));
    console.log(listFile);
    const pdf = listFile.find((file) => file === fileName.toString());
    if (pdf != undefined) {
      const directionFile = join(originFiles, pdf);
      const file = fs.createReadStream(directionFile);
      const mimetype = MIMETYPES[extname(directionFile)];
      return new StreamableFile(file, {
        type: mimetype,
        disposition: 'inline',
      });
    } else {
      throw new NotFoundException('Archivo no encontrado');
    }
  }
  async getFilesByDateRecipes(folderId: string, date: string) {
    const direcction = fs.readdirSync(
      join(__dirname, '..', '..', 'uploads', folderId, 'recipes_oac'),
    );
    const getfilesByDate = await Promise.all(
      direcction.map(async (file) => {
        const filePath = join(
          __dirname,
          '..',
          '..',
          'uploads',
          folderId,
          'recipes_oac',
          file,
        );
        const stats = await fsPromise.stat(filePath);
        console.log(stats.mtime.toISOString().split('.')[0]);
        if (stats.mtime.toISOString().split(':')[0] === date.split(':')[0]) {
          return {
            name: file,
            size: stats.size,
            createdAt: stats.mtime,
            updatedAt: stats.mtime,
          };
        }
      }),
    );
    return {
      success: true,
      files: getfilesByDate,
    };
  }
  async getFilesByDateDelivery(folderId: string, date: string) {
    const direcction = fs.readdirSync(
      join(__dirname, '..', '..', 'uploads', folderId, 'deliverys'),
    );
    try {
      const getfilesByDate = await Promise.all(
        direcction.map(async (file) => {
          const filePath = join(
            __dirname,
            '..',
            '..',
            'uploads',
            folderId,
            'deliverys_oac',
            file,
          );
          const stats = await fsPromise.stat(filePath);
          if (stats.mtime.toISOString().split(':')[0] === date.split(':')[0]) {
            return {
              name: file,
              size: stats.size,
              createdAt: stats.mtime,
              updatedAt: stats.mtime,
            };
          }
        }),
      );

      return {
        success: true,
        files: getfilesByDate,
      };
    } catch {
      throw new HttpException(
        'No hay Archivos en esta fecha',
        HttpStatus.AMBIGUOUS,
      );
    }
  }

  async findRecipesFarmacia(folderId: string) {
    const folderOriginRecipes = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'recipes_farmacia',
    );
    try {
      const listRecipes = await fsPromise.readdir(folderOriginRecipes);
      const filesInfo = await Promise.all(
        listRecipes.map(async (file) => {
          const filePath = join(folderOriginRecipes, file);
          const stats = await fsPromise.stat(filePath);
          return {
            name: file,
            size: stats.size,
            createdAt: stats.mtime,
            updatedAt: stats.mtime,
            direcction: stats.nlink,
          };
        }),
      );
      return {
        success: true,
        files: filesInfo,
      };
    } catch {
      throw new NotFoundException('No se encontró la carpeta de recetas');
    }
  }

  async streamFileFarmacia(folderId: string, fileName: string) {
    const MIMETYPES = {
      '.pdf': 'application/pdf',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
    };
    const originFiles = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'recipes_farmacia',
    );
    const listFile = await fsPromise.readdir(join(originFiles));
    console.log(listFile);
    const pdf = listFile.find((file) => file === fileName.toString());
    if (pdf != undefined) {
      const directionFile = join(originFiles, pdf);
      const file = fs.createReadStream(directionFile);
      const mimetype = MIMETYPES[extname(directionFile)];
      return new StreamableFile(file, {
        type: mimetype,
        disposition: 'inline',
      });
    } else {
      throw new NotFoundException('Archivo no encontrado');
    }
  }
  async findDeliverysFarmacia(folderId: string) {
    const folderOriginDelivery = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'deliverys_farmacia',
    );
    try {
      const listDelivery = await fsPromise.readdir(folderOriginDelivery);
      console.log(folderOriginDelivery);
      const filesInfo = await Promise.all(
        listDelivery.map(async (file) => {
          const filePath = join(folderOriginDelivery, file);
          const stats = await fsPromise.stat(filePath);
          return {
            name: file,
            size: stats.size,
            createdAt: stats.mtime,
            updatedAt: stats.mtime,
          };
        }),
      );
      return {
        success: true,
        files: filesInfo,
      };
    } catch {
      throw new NotFoundException('No se encontró la carpeta de Entregas');
    }
  }
  async streamFileDeliveryFarmacia(folderId: string, fileName: string) {
    const MIMETYPES = {
      '.pdf': 'application/pdf',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
    };
    const originFiles = join(
      __dirname,
      '..',
      '..',
      'uploads',
      folderId,
      'deliverys_farmacia',
    );
    const listFile = await fsPromise.readdir(join(originFiles));
    console.log(listFile);
    const pdf = listFile.find((file) => file === fileName.toString());
    if (pdf != undefined) {
      const directionFile = join(originFiles, pdf);
      const file = fs.createReadStream(directionFile);
      const mimetype = MIMETYPES[extname(directionFile)];
      return new StreamableFile(file, {
        type: mimetype,
        disposition: 'inline',
      });
    } else {
      throw new NotFoundException('Archivo no encontrado');
    }
  }
  async getFilesByDateRecipesFarmacia(folderId: string, date: string) {
    const direcction = fs.readdirSync(
      join(__dirname, '..', '..', 'uploads', folderId, 'recipes_farmacia'),
    );
    const getfilesByDate = await Promise.all(
      direcction.map(async (file) => {
        const filePath = join(
          __dirname,
          '..',
          '..',
          'uploads',
          folderId,
          'recipes_farmacia',
          file,
        );
        const stats = await fsPromise.stat(filePath);
        console.log(stats.mtime.toISOString().split('.')[0]);
        if (stats.mtime.toISOString().split(':')[0] === date.split(':')[0]) {
          return {
            name: file,
            size: stats.size,
            createdAt: stats.mtime,
            updatedAt: stats.mtime,
          };
        }
      }),
    );
    return {
      success: true,
      files: getfilesByDate,
    };
  }
  async getFilesByDateDeliveryFarmacia(folderId: string, date: string) {
    const direcction = fs.readdirSync(
      join(__dirname, '..', '..', 'uploads', folderId, 'deliverys_farmacia'),
    );
    try {
      const getfilesByDate = await Promise.all(
        direcction.map(async (file) => {
          const filePath = join(
            __dirname,
            '..',
            '..',
            'uploads',
            folderId,
            'deliverys_farmacia',
            file,
          );
          const stats = await fsPromise.stat(filePath);
          if (stats.mtime.toISOString().split(':')[0] === date.split(':')[0]) {
            return {
              name: file,
              size: stats.size,
              createdAt: stats.mtime,
              updatedAt: stats.mtime,
            };
          }
        }),
      );

      return {
        success: true,
        files: getfilesByDate,
      };
    } catch {
      throw new HttpException(
        'No hay Archivos en esta fecha',
        HttpStatus.AMBIGUOUS,
      );
    }
  }
}
