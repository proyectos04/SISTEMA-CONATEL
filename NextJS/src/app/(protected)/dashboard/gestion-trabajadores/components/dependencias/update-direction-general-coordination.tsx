import InputForm from "@/components/input-form";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState, useTransition } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import useSWR from "swr";
import {
  getCoordination,
  getDependency,
  getDirectionGeneralById,
  getDirectionLine,
} from "../../api/getInfoRac";
import upgradeDirectionGeneralCoordAction from "../../dependencias/actualizar-dependencia/actions/upgradeDirectionGeneralCoord";
import {
  SchemaUpgradeDireccionGeneralCoord,
  schemaUpgradeDireccionGeneralCoord,
} from "../../dependencias/actualizar-dependencia/schema/schemaUpdateDireccionGeneralCoord";
import Loading from "../loading/loading";

export default function UpdateDireccionGeneralCoordin() {
  const [isPending, startTransition] = useTransition();

  const [dependencyId, setDependencyId] = useState<number>(0);
  const { data: directionGeneral, isLoading: isLoadingDirectionGeneral } =
    useSWR(
      dependencyId ? ["directionGeneral", dependencyId] : null,
      async () => await getDirectionGeneralById(dependencyId),
    );
  const { data: dependency, isLoading: isLoadingDependency } = useSWR(
    "dependency",
    async () => await getDependency(),
  );

  const form = useForm<SchemaUpgradeDireccionGeneralCoord>({
    defaultValues: {
      Codigo: "",
      dependenciaId: 0,
      direccion_general: "",
      id: 0,
    },
    resolver: zodResolver(schemaUpgradeDireccionGeneralCoord),
  });
  const onSubmit = (values: SchemaUpgradeDireccionGeneralCoord) => {
    startTransition(async () => {
      const response = await upgradeDirectionGeneralCoordAction(values);
      if (response.success) {
        toast.success(response.message);
      } else {
        toast.error(response.message);
      }
    });
  };

  return (
    <>
      {isPending ? (
        <Loading />
      ) : (
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
            <FormField
              control={form.control}
              name="dependenciaId"
              render={({ field }) => (
                <FormItem className="col-span-2">
                  <FormLabel>Dependencia</FormLabel>
                  <Select
                    onValueChange={(values) => {
                      field.onChange(Number.parseInt(values));
                      setDependencyId(Number.parseInt(values));
                    }}
                  >
                    <FormControl>
                      <SelectTrigger className="w-full truncate">
                        <SelectValue
                          placeholder={`${isLoadingDependency ? "Cargando Depedencias" : "Seleccione una Dependencia"}`}
                        />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {dependency?.data.map((dependencia, i) => (
                        <SelectItem key={i} value={`${dependencia.id}`}>
                          {dependencia.Codigo}-{dependencia.dependencia}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Dirección General / Coordinación Adscrita
                  </FormLabel>
                  <Select
                    onValueChange={(values) => {
                      field.onChange(Number.parseInt(values));
                    }}
                  >
                    <FormControl>
                      <SelectTrigger className="w-full truncate">
                        <SelectValue
                          placeholder={`${isLoadingDirectionGeneral ? "Cargando Direcciones Generales" : "Seleccione una Dirección General"}`}
                        />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {directionGeneral?.data.map((general, i) => (
                        <SelectItem key={i} value={`${general.id}`}>
                          {general.Codigo}-{general.direccion_general}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <InputForm
              form={form}
              label="Codigo"
              nameInput="Codigo"
              type="number"
              placeholder="Ej. 00000000000"
            />
            <InputForm
              form={form}
              label="Nuevo nombre de la Dirección General / Coordinación Adscrita"
              nameInput="direccion_general"
              type="text"
              placeholder="Ej. Dirección General....."
            />
            <Button className="w-full"> Actualizar</Button>
          </form>
        </Form>
      )}
    </>
  );
}
