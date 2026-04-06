import z from "zod";

export const schemaUpgradeDireccionLineCoord = z.object({
  Codigo: z
    .string({
      required_error: "Este Campo Es Requerido",
    })
    .min(11, {
      message: "Minimo 12 Caracteres",
    })
    .refine((v) => Number.parseInt(v), {
      message: "Debe Ingresar Numeros",
    }),
  direccion_linea: z
    .string({
      required_error: "Este Campo Es Requerido",
    })
    .min(3, {
      message: "Minimo 3 Caracteres",
    }),
  dependenciaId: z.coerce
    .number({
      invalid_type_error: "Información Invalida",
    })
    .min(1, {
      message: "Debe Seleccionar Una Depedencia",
    }),
  direccionGeneral: z.coerce
    .number({
      invalid_type_error: "Información Invalida",
    })
    .min(1, {
      message: "Debe Seleccionar Una Dirección General / Coordinación Adscrita",
    }),
  id: z.coerce
    .number({
      invalid_type_error: "Información Invalida",
    })
    .min(1, {
      message:
        "Debe Seleccionar Una Direccion De Linea / Coordinación De Linea",
    }),
});

export type SchemaUpgradeDireccionLineCoord = z.infer<
  typeof schemaUpgradeDireccionLineCoord
>;
