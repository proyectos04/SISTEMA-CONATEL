import { GalleryVerticalEnd } from "lucide-react";

import { LoginForm } from "@/components/login-form";
import { Card } from "@/components/ui/card";
import Link from "next/link";
import Image from "next/image";

export default function LoginPage() {
  return (
    <Card className="grid h-[80%] lg:w-[70%] lg:grid-cols-2 p-0 backdrop-blur-3xl bg-slate-400/55 text-white border-0">
      <div className="flex flex-col p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-center ">
          <Link
            href="/login"
            className="flex  justify-center md:justify-center items-center gap-2 font-medium text-white w-[80%]"
          >
            <div className="bg-primary text-primary-foreground flex size-6 items-center justify-center rounded-md">
              <GalleryVerticalEnd className="size-4" />
            </div>
            Ministerio del Poder Popular para Relaciones Interiores, Justicia y
            Paz
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">
            <LoginForm />
          </div>
        </div>
      </div>
      <div className="bg-muted relative hidden lg:block">
        <Image
          height={2000}
          width={2000}
          src="/image (2).png"
          alt="Image"
          className="absolute inset-0 h-full w-full  dark:brightness-[0.2] dark:grayscale"
        />
      </div>
    </Card>
  );
}
