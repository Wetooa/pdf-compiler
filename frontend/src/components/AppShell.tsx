"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { getToken, clearToken } from "@/lib/auth";
import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/", label: "Home" },
  { href: "/process", label: "Process new" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (pathname !== "/login" && !getToken()) {
      router.replace("/login");
    }
  }, [pathname, router]);

  function logout() {
    clearToken();
    router.replace("/login");
  }

  const showNav = pathname !== "/login";

  return (
    <div className="min-h-screen bg-muted/30 text-foreground">
      <header className="sticky top-0 z-10 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <nav className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
          <Link
            href="/"
            className="flex items-center gap-2 text-xl font-semibold tracking-tight"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground text-sm font-medium">
              PDF
            </span>
            PDF Compiler
          </Link>
          {showNav && (
            <div className="flex items-center gap-1">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    buttonVariants({
                      variant: pathname === item.href ? "secondary" : "ghost",
                      size: "sm",
                    })
                  )}
                >
                  {item.label}
                </Link>
              ))}
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={logout}
              >
                Logout
              </Button>
            </div>
          )}
        </nav>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6">{children}</main>
    </div>
  );
}
