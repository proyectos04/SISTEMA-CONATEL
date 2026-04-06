"use client";
import {
  schemaCreateCoordinationDirection,
  schemaCreateDirectionGeneralDp,
  schemaCreateDirectionLineDirection,
} from "@/app/(protected)/dashboard/gestion-trabajadores/dependencias/crear-dependencia-direccion/schema/schemaCreateDirectionDependency";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState, useTransition } from "react";
import { useForm } from "react-hook-form";
import { Card, CardContent } from "../../../../../../components/ui/card";

import {
  createDirectionCordination,
  createDirectionGeneral,
  createDirectionLine,
} from "@/app/(protected)/dashboard/gestion-trabajadores/dependencias/crear-dependencia-direccion/action/createDirectionDependecy";
import {
  ApiResponse,
  DirectionGeneral,
  DirectionLine,
} from "@/app/types/types";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import z from "zod";
import {
  getDependency,
  getDirectionGeneral,
  getDirectionGeneralById,
  getDirectionLine,
} from "../../api/getInfoRac";
import Loading from "../loading/loading";
import { Button } from "../../../../../../components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../../../../../../components/ui/form";
import { Input } from "../../../../../../components/ui/input";
import { Label } from "../../../../../../components/ui/label";
import useSWR from "swr";

export default function FormCreateDirectionDependency() {
  const [isPending, startTransition] = useTransition();
  const [create, setCreate] = useState<string>("create-direction-general");
  const [dependencyId, setDependencyId] = useState<number | string>("");

  const [selectionDirectionGeneralId, setSelectionDirectionGeneralId] =
    useState<string>();

  const formDirectionGeneral = useForm({
    resolver: zodResolver(schemaCreateDirectionGeneralDp),
    defaultValues: {
      dependenciaId: 0,
      Codigo: "",
      direccion_general: "",
    },
  });
  const formDirection = useForm({
    resolver: zodResolver(schemaCreateDirectionLineDirection),
    defaultValues: {
      direccionGeneral: 0,
      Codigo: "",
      direccion_linea: "",
    },
  });
  const formCordination = useForm({
    resolver: zodResolver(schemaCreateCoordinationDirection),
    defaultValues: {
      direccionLinea: 0,
      Codigo: "",
      coordinacion: "",
    },
  });
  const { data: dependency, isLoading: isLoadingDependency } = useSWR(
    "dependency",
    async () => await getDependency(),
  );
  const { data: directionGeneral, isLoading: isLoadingDirectionGeneral } =
    useSWR(
      dependencyId ? ["directionGeneral", dependencyId] : null,
      async () => await getDirectionGeneralById(dependencyId),
    );

  const { data: directionLine, isLoading: isLoadingDirectionLine } = useSWR(
    selectionDirectionGeneralId
      ? ["directionLine", selectionDirectionGeneralId]
      : null,
    async () => await getDirectionLine(selectionDirectionGeneralId!),
  );
  const onSubmitDirectionGeneral = (
    values: z.infer<typeof schemaCreateDirectionGeneralDp>,
  ) => {
    startTransition(async () => {
      const response = await createDirectionGeneral(values);
      if (response.success) {
        toast.success(response.message);
        formDirectionGeneral.reset({
          Codigo: "",
          direccion_general: "",
          dependenciaId: 0,
        });
      } else {
        toast.error(response.message);
      }
    });
  };
  const onSubmitDirection = (
    values: z.infer<typeof schemaCreateDirectionLineDirection>,
  ) => {
    startTransition(async () => {
      const response = await createDirectionLine(values);
      if (response.success) {
        toast.success(response.message);
        formDirection.reset({
          Codigo: "",
          direccion_linea: "",
          direccionGeneral: 0,
        });
      } else {
        toast.error(response.message);
      }
    });
  };
  const onSubmitCordination = (
    values: z.infer<typeof schemaCreateCoordinationDirection>,
  ) => {
    startTransition(async () => {
      const response = await createDirectionCordination(values);
      if (response.success) {
        toast.success(response.message);
        formCordination.reset({
          Codigo: "",
          coordinacion: "",
          direccionLinea: 0,
        });
      } else {
        toast.error(response.message);
      }
    });
  };
  const selectionDependency = (id: number) => {
    formDirectionGeneral.setValue("dependenciaId", id);
  };
  const selectionDirectionGeneral = (id: number) => {
    formDirection.setValue("direccionGeneral", id);
  };
  const selectionDirectionLine = (id: number) => {
    formCordination.setValue("direccionLinea", id);
  };
  return (
    <>
      {isPending ? (
        <Loading />
      ) : (
        <>
          <Card>
            <CardContent className="space-y-6">
              <div className={"flex flex-col gap-2"}>
                <div className={`grid grid-cols-2 w-full gap-4`}>
                  <div
                    className={`space-y-2 ${(create === "create-coordination" || "create-direction-line") && ""}  ${create === "create-direction-general" && "col-span-2"}`}
                  >
                    <Label>Dependencia</Label>
                    <Select
                      onValueChange={(value) => {
                        setDependencyId(value);
                        selectionDependency(Number.parseInt(value));
                      }}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue
                          placeholder={`${isLoadingDependency ? "Cargando Dependencias" : "Seleccionar Dependencias"}`}
                        />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Dependencias</SelectLabel>
                          {dependency?.data.map((dp, i) => (
                            <SelectItem key={i} value={`${dp.id}`}>
                              {dp.Codigo}-{dp.dependencia}
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </div>
                  {create === "create-direction-line" && (
                    <div className="space-y-2">
                      <Label>Dirección General / Coordinación</Label>
                      <Select
                        onValueChange={(value) => {
                          selectionDirectionGeneral(Number.parseInt(value));
                        }}
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue
                            placeholder={`${isLoadingDirectionGeneral ? "Cargando Direcciones Generales" : "Seleccionar Dirección General"}`}
                          />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectGroup>
                            <SelectLabel>Direcciones De Generales </SelectLabel>
                            {directionGeneral?.data.map((general, i) => (
                              <SelectItem key={i} value={`${general.id}`}>
                                {general.Codigo}-{general.direccion_general}
                              </SelectItem>
                            ))}
                          </SelectGroup>
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                  {create === "create-coordination" && (
                    <>
                      <div className="space-y-2">
                        <Label>Dirección General / Coordinación</Label>
                        <Select
                          onValueChange={(value) => {
                            setSelectionDirectionGeneralId(value);
                            selectionDirectionGeneral(Number.parseInt(value));
                          }}
                        >
                          <SelectTrigger className="w-full">
                            <SelectValue
                              placeholder={`${isLoadingDirectionGeneral ? "Cargando Direcciones Generales" : "Seleccionar Dirección General"}`}
                            />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectGroup>
                              <SelectLabel>
                                Direcciones De Generales / Coordinación
                              </SelectLabel>
                              {directionGeneral?.data.map((general, i) => (
                                <SelectItem key={i} value={`${general.id}`}>
                                  {general.Codigo}-{general.direccion_general}
                                </SelectItem>
                              ))}
                            </SelectGroup>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2 col-span-2">
                        <Label>Dirección De Linea / Coordinación</Label>

                        <Select
                          onValueChange={(value) => {
                            selectionDirectionLine(Number.parseInt(value));
                          }}
                        >
                          <SelectTrigger className="w-full">
                            <SelectValue
                              placeholder={` ${isLoadingDirectionLine ? "Cargando Direcciones De Liena" : "Seleccionar Dirección De Linea"}`}
                            />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectGroup>
                              <SelectLabel>
                                Direcciones De Linea / Coordinaciones
                              </SelectLabel>
                              {directionLine?.data.map((line, i) => (
                                <SelectItem key={i} value={`${line.id}`}>
                                  {line.Codigo}-{line.direccion_linea}
                                </SelectItem>
                              ))}
                            </SelectGroup>
                          </SelectContent>
                        </Select>
                      </div>
                    </>
                  )}
                </div>

                <RadioGroup
                  defaultValue="create-direction-general"
                  onValueChange={(e) => setCreate(e)}
                  className="flex "
                >
                  <div className="flex items-center gap-3">
                    <RadioGroupItem
                      className="cursor-pointer"
                      value="create-direction-general"
                      id="r1"
                    />
                    <Label className="cursor-pointer" htmlFor="r1">
                      Crear Dirección General / Coordinación
                    </Label>
                  </div>
                  <div className="flex items-center gap-3">
                    <RadioGroupItem
                      className="cursor-pointer"
                      value="create-direction-line"
                      id="r2"
                    />
                    <Label className="cursor-pointer" htmlFor="r2">
                      Crear Dirección De Linea / Coordinación
                    </Label>
                  </div>
                  <div className="flex items-center gap-3">
                    <RadioGroupItem
                      className="cursor-pointer"
                      value="create-coordination"
                      id="r3"
                    />
                    <Label className="cursor-pointer" htmlFor="r3">
                      Crear Coordinación
                    </Label>
                  </div>
                </RadioGroup>
              </div>
              {create === "create-direction-general" && (
                <div>
                  <Form {...formDirectionGeneral}>
                    <form
                      onSubmit={formDirectionGeneral.handleSubmit(
                        onSubmitDirectionGeneral,
                      )}
                      className="space-y-5"
                    >
                      <div className="grid grid-cols-2  place-content-stretch place-items-start gap-3 w-full  ">
                        <FormField
                          name="Codigo"
                          control={formDirectionGeneral.control}
                          render={({ field }) => (
                            <FormItem className="w-full truncate p-0.5">
                              <FormLabel>
                                Codigo de la Dirección General / Coordinación
                              </FormLabel>
                              <FormControl>
                                <Input {...field} type="number" />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          name="direccion_general"
                          control={formDirectionGeneral.control}
                          render={({ field }) => (
                            <FormItem className="w-full truncate p-0.5">
                              <FormLabel>
                                Nombre De La Dirección General / Coordinación
                              </FormLabel>
                              <FormControl>
                                <Input {...field} />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      <Button className="w-full">
                        Crear Dirección General / Coordinación
                      </Button>
                    </form>
                  </Form>
                </div>
              )}
              {create === "create-direction-line" && (
                <div>
                  <Form {...formDirection}>
                    <form
                      onSubmit={formDirection.handleSubmit(onSubmitDirection)}
                      className="space-y-5"
                    >
                      <div className="grid grid-cols-2  place-content-stretch place-items-start gap-3 w-full  ">
                        <FormField
                          name="Codigo"
                          control={formDirection.control}
                          render={({ field }) => (
                            <FormItem className="w-full truncate p-0.5">
                              <FormLabel>
                                Código De La Dirección De Linea / Coordinación
                              </FormLabel>
                              <FormControl>
                                <Input {...field} type="number" />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          name="direccion_linea"
                          control={formDirection.control}
                          render={({ field }) => (
                            <FormItem className="w-full truncate p-0.5">
                              <FormLabel>
                                Nombre De La Dirección De Linea / Coordinación
                              </FormLabel>
                              <FormControl>
                                <Input {...field} />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      <Button className="w-full">
                        Crear Dirección De Linea / Coordinación
                      </Button>
                    </form>
                  </Form>
                </div>
              )}
              {create === "create-coordination" && (
                <div>
                  <Form {...formCordination}>
                    <form
                      onSubmit={formCordination.handleSubmit(
                        onSubmitCordination,
                      )}
                      className="space-y-5"
                    >
                      <div className="grid grid-cols-2  place-content-stretch place-items-start gap-3 w-full ">
                        <FormField
                          name="Codigo"
                          control={formCordination.control}
                          render={({ field }) => (
                            <FormItem className="w-full truncate p-0.5">
                              <FormLabel>Código De La Coordinación</FormLabel>
                              <FormControl>
                                <Input {...field} type="number" />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          name="coordinacion"
                          control={formCordination.control}
                          render={({ field }) => (
                            <FormItem className="w-full truncate p-0.5">
                              <FormLabel>Nombre De La Coordinación</FormLabel>
                              <FormControl>
                                <Input {...field} />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      <Button className="w-full">Crear Coordinación</Button>
                    </form>
                  </Form>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </>
  );
}
