"use client";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent } from "../../../../../../components/ui/card";
import { Label } from "../../../../../../components/ui/label";

import {
  getCoordination,
  getDependency,
  getDirectionGeneralById,
  getDirectionLine,
} from "@/app/(protected)/dashboard/gestion-trabajadores/api/getInfoRac";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useMemo, useState } from "react";
import useSWR from "swr";
import Error from "../error/error";
export default function TableDependencys() {
  const [dependencyId, setDependencyId] = useState<number | string>("");
  const [directionGeneralId, setDirectionGeneralId] = useState<string | null>(
    null,
  );
  const [coordinationId, setCoordinationId] = useState<string | null>(null);

  const { data: dependency, isLoading: isLoadingDependency } = useSWR(
    "dependency",
    async () => await getDependency(),
  );
  const { data: directionGeneral, isLoading: isLoadingDirectionGeneral } =
    useSWR(
      dependencyId ? [`directionGeneral.${dependencyId}`, dependencyId] : null,
      async () => await getDirectionGeneralById(dependencyId),
    );
  const coordinationGeneral = useMemo(() => {
    if (!directionGeneral?.data) return [];
    return directionGeneral.data.filter((v) => {
      // Added optional chaining here: v.Codigo?.at(-1)
      const lasNumber = v.Codigo?.at(-1);
      return Number.parseInt(lasNumber ?? "0") > 0;
    });
  }, [directionGeneral]);

  const { data: directionLine } = useSWR(
    directionGeneralId
      ? [
          `directionLine.${dependencyId}.${directionGeneralId}`,
          dependencyId,
          directionGeneralId,
        ]
      : null,
    async () => await getDirectionLine(directionGeneralId!),
  );
  const coordinationLine = useMemo(() => {
    if (!directionLine?.data) return [];
    return directionLine.data.filter((v) => {
      const lasNumber = v.Codigo?.at(-1);
      return Number.parseInt(lasNumber ?? "0") > 0;
    });
  }, [directionLine]);
  const { data: coordination } = useSWR(
    coordinationId
      ? [
          `coordination.${dependencyId}.${directionGeneralId}.${coordinationId}`,
          dependencyId,
          directionGeneralId,
          coordinationId,
        ]
      : null,
    async () => await getCoordination(coordinationId!),
  );

  return (
    <>
      <Card>
        <CardContent>
          <div className={`grid grid-cols-2 w-full gap-4 space-y-5`}>
            <div className={`col-span-2 space-y-2`}>
              <Label>Dependencia</Label>
              <Select
                onValueChange={(value) => {
                  setDependencyId(value);
                }}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Seleccionar Dependencia" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Direcciones De Generales</SelectLabel>
                    {dependency?.data.map((dp, i) => (
                      <SelectItem key={i} value={`${dp.id}`}>
                        {dp.Codigo}-{dp.dependencia}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
                <div className="text-sm text-gray-700 text-[12px]">
                  Consultar Coordinaciones Adscritas al Despacho /
                  Viceministerio
                </div>
              </Select>
            </div>

            <div className={`space-y-2 `}>
              <Label>Dirección General / Coordinación</Label>
              <Select
                onValueChange={(value) => {
                  setDirectionGeneralId(value);
                }}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Seleccionar Dirección General" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>
                      Direcciones De General / Coordinación
                    </SelectLabel>
                    {directionGeneral?.data.map((general, i) => (
                      <SelectItem key={i} value={`${general.id}`}>
                        {general.Codigo}-{general.direccion_general}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
                <div className="text-sm text-gray-700 text-[12px]">
                  Consultar Coordinaciones Adscritas a la Direccion General
                </div>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Dirección De Linea / Coordinacion</Label>

              <Select
                onValueChange={(value) => {
                  setCoordinationId(value);
                }}
              >
                <SelectTrigger
                  className="w-full"
                  disabled={
                    directionLine?.data !== undefined &&
                    directionLine!.data?.length > 0
                      ? false
                      : true
                  }
                >
                  <SelectValue
                    placeholder={`${directionLine?.data !== undefined && directionLine!.data?.length > 0 ? "Seleccionar Dirección De Linea" : "No Posee Direcciones De Linea"}`}
                  />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Dirección De Linea / Coordinacion</SelectLabel>
                    {directionLine?.data.map((line, i) => (
                      <SelectItem key={i} value={`${line.id}`}>
                        {line.Codigo}-{line.direccion_linea}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
                <div className="text-[12px] text-gray-700">
                  Consultar Coordinaciones De La Dirección De Linea
                </div>
              </Select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-5 ">
            {coordinationGeneral.length > 0 &&
              Array.isArray(coordinationGeneral) && (
                <div className="overflow-auto h-70  border rounded-2xl border-blue-700 col-span-2 ">
                  <Table>
                    <TableCaption>
                      Coordinaciones adscritas al Despacho/Viceministerio
                    </TableCaption>
                    <TableHeader className="bg-blue-600">
                      <TableRow>
                        <TableHead className="w-[100px] font-bold text-white">
                          Código
                        </TableHead>
                        <TableHead className="text-center font-bold text-white">
                          Coordinaciones adscritas al Despacho/Viceministerio
                        </TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {coordinationGeneral?.map((general, i) => (
                        <TableRow key={i}>
                          <TableCell className="font-medium">
                            {general.Codigo}
                          </TableCell>
                          <TableCell className="text-center">
                            {general.direccion_general}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}

            <div className=" h-70     rounded-2xl">
              {coordinationLine.length > 0 &&
                Array.isArray(coordinationLine) && (
                  <div className="border overflow-auto border-blue-600 rounded-2xl">
                    <Table>
                      <TableCaption>Coordinaciones De Lineas</TableCaption>
                      <TableHeader className="bg-blue-600 ">
                        <TableRow>
                          <TableHead className="w-[100px] font-bold text-white">
                            Código
                          </TableHead>
                          <TableHead className="text-center font-bold text-white ">
                            Coordinación De Linea
                          </TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {coordinationLine?.map((direction, i) => (
                          <TableRow key={i}>
                            <TableCell className="font-medium">
                              {direction.Codigo}
                            </TableCell>
                            <TableCell className="text-center">
                              {direction.direccion_linea}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
            </div>
            <div className="h-70   rounded-2xl">
              {coordination?.data.length! > 0 && (
                <div className="border overflow-auto border-blue-600 rounded-2xl">
                  <Table>
                    <TableCaption>Coordinaciones</TableCaption>
                    <TableHeader className="bg-blue-600">
                      <TableRow>
                        <TableHead className="w-[100px] font-bold text-white">
                          Código
                        </TableHead>
                        <TableHead className="text-center font-bold text-white">
                          Coordinación
                        </TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {coordination?.data.map((coordination, i) => (
                        <TableRow key={i}>
                          <TableCell className="font-medium">
                            {coordination.Codigo}
                          </TableCell>
                          <TableCell className="text-center">
                            {coordination.coordinacion}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </>
  );
}
