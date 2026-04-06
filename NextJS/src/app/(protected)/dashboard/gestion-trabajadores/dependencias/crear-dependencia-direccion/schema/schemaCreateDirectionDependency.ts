import z from "zod";

export const schemaCreateDirectionGeneralDp = z.object({
  dependenciaId: z.number(),
  Codigo: z
    .string({
      message: "Datos Incorrecos",
      required_error: "Datos Invalidos",
    })
    .trim()

    .min(12, {
      message: "Minimo 12 Caracteres",
    }),
  direccion_general: z
    .string({
      message: "Datos Incorrecos",
      required_error: "Datos Invalidos",
    })
    .min(12, {
      message: "Minimo 12 Caracteres",
    }),
});
export const schemaCreateDirectionLineDirection = z.object({
  direccionGeneral: z.number(),
  Codigo: z
    .string({
      message: "Datos Incorrecos",
      required_error: "Datos Invalidos",
    })
    .min(12, {
      message: "Minimo 12 Caracteres",
    }),
  direccion_linea: z
    .string({
      message: "Datos Incorrecos",
      required_error: "Datos Invalidos",
    })
    .min(12, {
      message: "Minimo 12 Caracteres",
    }),
});
export const schemaCreateCoordinationDirection = z.object({
  direccionLinea: z.number(),
  Codigo: z
    .string({
      message: "Datos Incorrecos",
      required_error: "Datos Invalidos",
    })
    .min(12, {
      message: "Minimo 12 Caracteres",
    }),
  coordinacion: z
    .string({
      message: "Datos Incorrecos",
      required_error: "Datos Invalidos",
    })
    .min(12, {
      message: "Minimo 12 Caracteres",
    }),
});
