"use server";

import z from "zod";
import { schemaFamilyEmployeeOne } from "../schema/schemaCreateFamily";
import { auth } from "#/auth";
import { ApiResponse } from "@/app/types/types";

export default async function createFamilyPasiveActions(
  values: z.infer<typeof schemaFamilyEmployeeOne>,
  id: string | number,
) {
  try {
    const session = await auth();
    if (!session || !session.user?.id) {
      return {
        success: false,
        message: "No tienes permiso para realizar esta acción. Inicia sesión.",
      };
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_DJANGO_API_URL_SERVER}Employeefamily/${id}/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ...values, usuario_id: session.user.id }),
      },
    );
    const getResponse: ApiResponse<never> = await response.json();
    if (response.ok) {
      return {
        success: true,
        message: getResponse.message,
      };
    }
    return {
      success: false,
      message: getResponse.message,
    };
  } catch {
    return {
      success: false,
      message: "Ocurrio un error",
    };
  }
}
