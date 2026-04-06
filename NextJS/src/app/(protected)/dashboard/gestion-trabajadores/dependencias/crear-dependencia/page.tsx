import CreateDependency from "../../components/dependencias/create-dependency";
import PageLayout from "../../../../../../components/layout/page-layout";

export default function Dependencys() {
  return (
    <PageLayout
      title="Gestión de Dependencias"
      description="Registre Nuevas Dependencias Para Empleados"
    >
      <CreateDependency />
    </PageLayout>
  );
}
