"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  listBatches,
  downloadCompiledPdf,
  deleteBatch,
  SessionExpiredError,
  type BatchMeta,
} from "@/lib/api";
import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

function statusVariant(status: BatchMeta["status"]): "default" | "destructive" | "secondary" {
  if (status === "completed" || status === "completed_with_errors") return "default";
  if (status === "failed") return "destructive";
  return "secondary";
}

export default function HomePage() {
  const [batches, setBatches] = useState<BatchMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadBatches();
  }, []);

  async function loadBatches() {
    setLoading(true);
    setError("");
    try {
      const data = await listBatches();
      setBatches(data);
    } catch (e) {
      if (e instanceof SessionExpiredError) return;
      setError(e instanceof Error ? e.message : "Failed to load batches");
      setBatches([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(batch: BatchMeta) {
    if (!confirm("Delete this batch? This cannot be undone.")) return;
    try {
      await deleteBatch(batch.id);
      setBatches((prev) => prev.filter((b) => b.id !== batch.id));
    } catch (e) {
      if (e instanceof SessionExpiredError) return;
      setError(e instanceof Error ? e.message : "Failed to delete batch");
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">
          Your processed batches
        </h1>
        <p className="text-sm text-muted-foreground">
          View and download compiled learning guides from your PDF batches.
        </p>
      </div>

      {loading && (
        <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="border border-border shadow-lg">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 px-5 py-3">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="h-5 w-16 rounded-full" />
              </CardHeader>
              <CardContent className="px-5 py-3">
                <Skeleton className="h-4 w-full max-w-[200px]" />
              </CardContent>
              <CardFooter className="flex gap-2 px-5 py-4">
                <Skeleton className="h-8 w-16" />
                <Skeleton className="h-8 w-24" />
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {!loading && error && (
        <Card className="border border-border border-destructive/50 shadow-lg">
          <CardContent className="px-5 py-4">
            <p className="text-sm text-destructive">{error}</p>
            <Button
              className="mt-3"
              onClick={loadBatches}
              variant="outline"
              size="sm"
            >
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {!loading && !error && batches.length === 0 && (
        <Card className="border border-border shadow-lg">
          <CardContent className="flex flex-col items-center justify-center px-5 py-12 text-center">
            <div
              className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-muted text-muted-foreground"
              aria-hidden
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-7 w-7"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <p className="mb-1 font-medium text-foreground">No batches yet</p>
            <p className="mb-6 max-w-sm text-sm text-muted-foreground">
              Upload PDFs to generate simplified learning guides. Processing runs
              in the background.
            </p>
            <Link
              href="/process"
              className={cn(buttonVariants({ variant: "default" }))}
            >
              Process your first PDFs
            </Link>
          </CardContent>
        </Card>
      )}

      {!loading && !error && batches.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2">
          {batches.map((batch) => (
            <Card
              key={batch.id}
              className="border border-border shadow-lg transition-shadow hover:shadow-md"
            >
              <CardHeader className="px-5 py-3">
                <CardTitle className="text-base">{batch.name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1.5 px-5 py-3">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm text-muted-foreground">
                    {batch.pdf_count} PDF(s)
                  </p>
                  <Badge variant={statusVariant(batch.status)}>
                    {batch.status.replace("_", " ")}
                  </Badge>
                </div>
              </CardContent>
              <CardFooter className="flex flex-wrap gap-2 px-5 py-4">
                <Link
                  href={`/batches/${batch.id}`}
                  className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
                >
                  View
                </Link>
                {(batch.status === "completed" ||
                  batch.status === "completed_with_errors") &&
                  batch.compiled_pdf && (
                    <Button
                      type="button"
                      variant="default"
                      size="sm"
                      onClick={() => downloadCompiledPdf(batch.id)}
                    >
                      Download PDF
                    </Button>
                  )}
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  onClick={() => handleDelete(batch)}
                >
                  Delete
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
