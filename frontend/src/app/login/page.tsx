"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { setToken } from "@/lib/auth";
import { login } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!password.trim()) return;
    setError("");
    setSubmitting(true);
    try {
      const { token } = await login(password);
      setToken(token);
      router.replace("/");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Invalid password");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center bg-muted/40 px-6 py-12">
      <Card className="w-full max-w-sm border border-border shadow-lg gap-3 px-8 py-6">
        <CardHeader className="space-y-1.5 px-0 pt-0 pb-3">
          <CardTitle>PDF Compiler</CardTitle>
          <CardDescription>Enter the password to continue.</CardDescription>
        </CardHeader>
        <form onSubmit={onSubmit}>
          <CardContent className="space-y-4 px-0 pt-0 pb-2">
            <div className="space-y-2">
              <label
                htmlFor="password"
                className="text-sm font-medium"
              >
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                autoComplete="current-password"
                disabled={submitting}
                className="h-10 px-3 py-2"
              />
            </div>
            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
          </CardContent>
          <CardFooter className="flex flex-col gap-4 px-0 pt-2 pb-0">
            <Button
              type="submit"
              className="w-full"
              disabled={submitting || !password.trim()}
            >
              {submitting ? "Signing in…" : "Sign in"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
