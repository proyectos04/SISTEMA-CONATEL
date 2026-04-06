"use client";
import PageLayout from "@/components/layout/page-layout";
import TableUser from "./tableUser/page";
import useSWR from "swr";
import { getUserListPasiveSearch } from "../../api/getInfo";
import z from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form } from "@/components/ui/form";
import { useState } from "react";
import Loading from "../../../gestion-trabajadores/components/loading/loading";
import InputForm from "@/components/input-form";
import { Button } from "@/components/ui/button";
import { CircleEllipsis, Search } from "lucide-react";

export default function UsersPage() {
  const [searchParams, setSearchParams] = useState<string>();
  const {
    data: user,
    isLoading: isLoadingUser,
    mutate,
  } = useSWR(
    `/api/users/${searchParams}`,
    async () => await getUserListPasiveSearch({ searchParams }),
  );
  const schemaSearch = z.object({
    cedulaidentidad: z.string(),
  });
  const onSearch = (values: z.infer<typeof schemaSearch>) => {
    const filteredEntries = Object.entries(values).filter(
      ([_, v]) => v !== "" && v !== undefined && v !== null,
    );
    const params = new URLSearchParams(filteredEntries as unknown as string);
    setSearchParams(params.toString());
  };
  const form = useForm<z.infer<typeof schemaSearch>>({
    defaultValues: {
      cedulaidentidad: "",
    },
    resolver: zodResolver(schemaSearch),
  });
  const onClean = () => {
    form.reset({
      cedulaidentidad: "",
    });
  };
  return (
    <PageLayout title="Usuarios">
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSearch)}
          className="flex gap-2 align-baseline items-center"
        >
          <InputForm
            form={form}
            label="Cedula"
            nameInput="cedulaidentidad"
            type="text"
          />
          <Button className="self-baseline-last" type="submit">
            <Search />
            Buscar
          </Button>
          <Button
            onClick={onClean}
            className="self-baseline-last"
            type="button"
            variant={"outline"}
          >
            <CircleEllipsis />
            Limpiar
          </Button>
        </form>
      </Form>
      {isLoadingUser ? <Loading /> : <TableUser user={user?.data ?? []} />}
    </PageLayout>
  );
}
