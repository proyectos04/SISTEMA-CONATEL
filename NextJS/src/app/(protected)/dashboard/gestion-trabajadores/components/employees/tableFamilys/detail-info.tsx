"use client";
import { Family } from "@/app/types/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  SheetContentUI,
  SheetHeaderUI,
  SheetTitleUI,
  SheetTriggerUI,
  SheetUI,
} from "@/components/ui/SheetUI";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { format } from "date-fns";
import { formatInTimeZone } from "date-fns-tz";
import {
  Ambulance,
  GraduationCap,
  Heart,
  PersonStanding,
  ShipIcon,
  ShipWheel,
  Shirt,
} from "lucide-react";
import UpdateBasicInfoFamily from "./updateInfo/form/form-update-info";
import FormRelationship from "./updateInfo/form/form-relationship";
import UpdateFormPhysical from "./updateInfo/form/form-physical-update";
import UpdateFormAcademy from "./updateInfo/form/form-academy-update";
import FormUpdateHealthFamily from "./updateInfo/form/form-health_profile";
interface Props {
  family: Family;
}
export function DetailInfoFamily({ family }: Props) {
  return (
    <SheetUI>
      <SheetTriggerUI asChild>
        <Button className="w-full">Ver Detalles</Button>
      </SheetTriggerUI>
      <SheetContentUI>
        <SheetHeaderUI>
          <SheetTitleUI>Información Detallada Del Familiar</SheetTitleUI>
        </SheetHeaderUI>
        <ScrollArea className="space-y-5 h-[90%]">
          <div className="space-y-5">
            <Card>
              <CardHeader className="flex justify-between">
                <div className="flex flex-row justify-between gap-2">
                  Información Basica
                  <PersonStanding />
                </div>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant={"default"} size={"sm"}>
                      Editar
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <UpdateBasicInfoFamily id={family.id} />
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2">
                  <span>Cedula</span>
                  <span>{family.cedulaFamiliar}</span>
                  <span>Primer Nombre</span>
                  <span>{family.primer_nombre}</span>
                  <span>Segundo Nombre</span>
                  <span>{family.segundo_nombre ?? "N/A"}</span>
                  <span>Primer Apellido</span>
                  <span>{family.primer_apellido}</span>
                  <span>Segundo Apellido</span>
                  <span>{family.segundo_apellido ?? "N/A"}</span>
                  <span>F. Nacimiento</span>
                  <span>
                    {format(
                      new Date(family.fechanacimiento).toISOString(),
                      "dd/MM/yyyy",
                    )}
                  </span>
                  <span>Sexo</span>
                  <span>{family.sexo.sexo}</span>
                  <span>Estado Civil</span>
                  <span>{family.estadoCivil?.estadoCivil}</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row justify-between">
                <div className="flex flex-row gap-2 items-center">
                  Relacion/Parentesco
                  <PersonStanding />
                </div>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant={"default"} size={"sm"}>
                      Editar
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <FormRelationship id={family.id} />
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2">
                  <span>Parentesco</span>
                  <span>
                    {family.parentesco?.descripcion_parentesco ?? "N/A"}
                  </span>
                  <span>Labora en la Institución </span>
                  <span>
                    <Badge
                      variant={family.mismo_ente ? "default" : "destructive"}
                    >
                      {family.mismo_ente
                        ? "Trabaja en la Institucion"
                        : "No Trabaja en la Institucion"}
                    </Badge>
                  </span>
                  <span>Heredero </span>
                  <span>
                    <Badge
                      variant={family.heredero ? "default" : "destructive"}
                    >
                      {family.heredero ? "Heredero" : "No es heredero"}
                    </Badge>
                  </span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="flex flex-row items-center gap-3 justify-between">
                  <div className="flex items-center gap-2">
                    Formaciones Academicas <GraduationCap />
                  </div>
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant={"default"} size={"sm"}>
                        Editar
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <UpdateFormAcademy id={family.id} />
                    </DialogContent>
                  </Dialog>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 place-content-center">
                  <div>Nivel Academico:</div>
                  <div>
                    {family.formacion_academica_familiar?.nivelAcademico
                      ?.nivelacademico ?? "N/A"}
                  </div>
                  <div>Carrera:</div>
                  <div>
                    {family.formacion_academica_familiar?.carrera
                      ?.nombre_carrera ?? "N/A"}
                  </div>
                  <div>Mención:</div>
                  <div>
                    {family.formacion_academica_familiar?.mension
                      ?.nombre_mencion ?? "N/A"}
                  </div>
                  <div>Institución:</div>
                  <div>
                    {family.formacion_academica_familiar?.institucion ?? "N/A"}
                  </div>

                  <div>Capacitación</div>
                  <div>
                    {family.formacion_academica_familiar?.capacitacion ?? "N/A"}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex flex-row items-center gap-3 justify-between">
                  <div className="flex flex-row items-center gap-2">
                    Información De Vestimenta <Shirt />
                  </div>
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant={"default"} size={"sm"}>
                        Editar
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <UpdateFormPhysical id={family.id} />
                    </DialogContent>
                  </Dialog>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 place-content-center">
                  <div>Talla De Camisa:</div>
                  <div>
                    {family.perfil_fisico_familiar?.tallaCamisa?.talla ?? "N/A"}
                  </div>
                  <div>Talla de Pantalon:</div>
                  <div>
                    <div>
                      {family.perfil_fisico_familiar?.tallaPantalon?.talla ??
                        "N/A"}
                    </div>
                  </div>
                  <div>Talla De Calzado:</div>
                  <div>
                    <div>
                      {family.perfil_fisico_familiar?.tallaZapatos?.talla ??
                        "N/A"}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <CardHeader className="flex flex-row justify-between">
              <div className=" flex flex-row items-center gap-2 ">
                Información De Salud <Heart />
              </div>
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant={"default"} size={"sm"}>
                    Editar
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <FormUpdateHealthFamily id={family.id} />
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 place-content-center">
                <div>Tipo De Sangre:</div>
                <div>
                  {family.perfil_salud_familiar?.grupoSanguineo != null
                    ? family.perfil_salud_familiar.grupoSanguineo.grupoSanguineo
                    : "N/A"}
                </div>
                {family.perfil_salud_familiar?.patologiasCronicas &&
                  family.perfil_salud_familiar.patologiasCronicas.length >
                    0 && (
                    <Table className="col-span-2">
                      <TableCaption>
                        Lista De Patologias Del Trabajador
                      </TableCaption>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Categoria</TableHead>
                          <TableHead>Patologia</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {family.perfil_salud_familiar.patologiasCronicas.map(
                          (v, i) => (
                            <TableRow key={i}>
                              <TableCell className="font-medium">
                                {v.categoria.nombre_categoria}
                              </TableCell>
                              <TableCell>{v.patologia}</TableCell>
                            </TableRow>
                          ),
                        )}
                      </TableBody>
                    </Table>
                  )}
                {family.perfil_salud_familiar?.discapacidad &&
                  family.perfil_salud_familiar.discapacidad.length > 0 && (
                    <Table className="col-span-2">
                      <TableCaption>
                        Lista De Discapcidades Del Trabajador
                      </TableCaption>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Categoria</TableHead>
                          <TableHead>Discapacidad</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {family.perfil_salud_familiar.discapacidad.map(
                          (v, i) => (
                            <TableRow key={i}>
                              <TableCell className="font-medium">
                                {v.categoria.nombre_categoria}
                              </TableCell>
                              <TableCell>{v.discapacidad}</TableCell>
                            </TableRow>
                          ),
                        )}
                      </TableBody>
                    </Table>
                  )}
                {family.perfil_salud_familiar?.alergias &&
                  family.perfil_salud_familiar.alergias.length > 0 && (
                    <div className="col-span-2">
                      <Table>
                        <TableCaption>
                          Lista De Patologias Del Trabajador
                        </TableCaption>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Categoria</TableHead>
                            <TableHead>Alergias</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {family.perfil_salud_familiar.alergias.map((v, i) => (
                            <TableRow key={i}>
                              <TableCell className="font-medium">
                                {v.categoria.nombre_categoria}
                              </TableCell>
                              <TableCell>{v.alergia}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  )}
              </div>
            </CardContent>
          </div>
        </ScrollArea>
      </SheetContentUI>
    </SheetUI>
  );
}
