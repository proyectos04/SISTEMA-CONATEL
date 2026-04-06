import { ApiResponse, Depart, Role, UserSystem } from "@/app/types/types";
import { apiFetchGet } from "@/lib/utils";

export const getDeparment = async () => {
  return await apiFetchGet<Depart[]>("accounts/departamentos/");
};
export const getRole = async () => {
  return await apiFetchGet<Role[]>("accounts/roles/");
};

export const getUserListPasiveSearch = async ({
  searchParams,
}: {
  searchParams: string | undefined;
}): Promise<ApiResponse<UserSystem[]>> => {
  return await apiFetchGet<UserSystem[]>(`accounts/usuarios/?${searchParams}`);
};
