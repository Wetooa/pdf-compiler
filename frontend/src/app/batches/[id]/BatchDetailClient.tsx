"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  getBatch,
  downloadCompiledPdf,
  openSourcePdf,
  deleteBatch,
  type BatchMeta,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
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

export default function BatchDetailClient() {
  const params = useParams();
  const router = useRouter();
  const batchId = typeof params.id === "string" ? params.id : "";
  const [batch, setBatch] = useState<BatchMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!batchId) return;
    let cancelled = false;

    async function poll(isInitial: boolean) {
      if (isInitial) {
        setLoading(true);
        setError("");
      }
      try {
        const b = await getBatch(batchId);
        if (cancelled) return;
        setBatch(b);
        setLoading(false);
        if (b.status === "processing") {
          setTimeout(() => poll(false), 3000);
        }
      } catch (e: unknown) {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : "Failed to load batch");
        setLoading(false);
      }
    }

    poll(true);
    return () => {
      cancelled = true;
    };
  }, [batchId]);

  async function handleDelete() {
    if (!confirm("Delete this batch? This cannot be undone.")) return;
    try {
      await deleteBatch(batchId);
      router.replace("/");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete batch");
    }
  }

  return (
    <div className="space-y-6">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground"
      >
        ← Back to batches
      </Link>

      {error && (
        <Card className="border border-border border-destructive/50 shadow-lg">
          <CardContent className="px-5 py-4">
            <p className="text-sm text-destructive">{error}</p>
            <Button
              className="mt-3"
              onClick={() => window.location.reload()}
              variant="outline"
              size="sm"
            >
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {loading && !batch && (
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <Card className="border border-border shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 px-5 py-3">
              <Skeleton className="h-5 w-20" />
              <Skeleton className="h-5 w-24 rounded-full" />
            </CardHeader>
            <CardContent className="space-y-1.5 px-5 py-3">
              <Skeleton className="h-4 w-full max-w-md" />
              <Skeleton className="h-4 w-64" />
            </CardContent>
          </Card>
        </div>
      )}

      {batch && (
        <>
          <div className="flex flex-col gap-2">
            <h1 className="text-2xl font-semibold tracking-tight">
              {batch.name}
            </h1>
            <p className="text-sm text-muted-foreground">
              Batch ID: {batch.id.slice(0, 8)}…
            </p>
          </div>

          <Card className="border border-border shadow-lg">
            <CardHeader className="px-5 py-3">
              <CardTitle>Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1.5 px-5 py-3">
              <div className="flex flex-wrap items-center gap-2">
                {batch.status === "processing" && (
                  <>
                    <p className="text-muted-foreground">
                      Processing {batch.pdf_count} PDF(s). This may take several
                      minutes.
                    </p>
                    <Badge variant={statusVariant(batch.status)}>
                      {batch.status.replace("_", " ")}
                    </Badge>
                  </>
                )}
                {batch.status === "failed" && batch.error && (
                  <>
                    <p className="text-destructive">{batch.error}</p>
                    <Badge variant={statusVariant(batch.status)}>
                      {batch.status.replace("_", " ")}
                    </Badge>
                  </>
                )}
                {(batch.status === "completed" ||
                  batch.status === "completed_with_errors") && (
                  <>
                    <p className="text-muted-foreground">
                      {batch.pdf_count} PDF(s) processed.
                      {batch.failed_count ? (
                        <span className="text-destructive">
                          {" "}
                          {batch.failed_count} failed.
                        </span>
                      ) : null}
                    </p>
                    <Badge variant={statusVariant(batch.status)}>
                      {batch.status.replace("_", " ")}
                    </Badge>
                  </>
                )}
              </div>
              {batch.status === "processing" && (
                <p className="text-sm text-muted-foreground">
                  Page will refresh automatically.
                </p>
              )}
            </CardContent>
          </Card>

          {batch.pdf_names && batch.pdf_names.length > 0 && (
            <Card className="border border-border shadow-lg">
              <CardHeader className="px-5 py-3">
                <CardTitle>PDFs in this batch</CardTitle>
              </CardHeader>
              <CardContent className="px-5 py-3">
                <ul className="space-y-1.5 text-sm text-muted-foreground">
                  {batch.pdf_names.map((pdfName) => (
                    <li
                      key={pdfName}
                      className="flex items-center justify-between gap-2 rounded-md py-0.5"
                    >
                      <span className="min-w-0 truncate">{pdfName}</span>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => openSourcePdf(batchId, pdfName)}
                      >
                        View
                      </Button>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {(batch.status === "completed" ||
            batch.status === "completed_with_errors") &&
            batch.compiled_pdf && (
              <Card className="border border-border shadow-lg">
                <CardHeader className="space-y-1 px-5 py-3">
                  <CardTitle>Download</CardTitle>
                  <CardDescription>
                    Your compiled learning guide PDF is ready.
                  </CardDescription>
                </CardHeader>
                <CardFooter className="px-5 py-4">
                  <Button
                    type="button"
                    onClick={() => downloadCompiledPdf(batchId)}
                  >
                    Download compiled PDF
                  </Button>
                </CardFooter>
              </Card>
            )}

          <div className="pt-4">
            <Button
              type="button"
              variant="destructive"
              onClick={handleDelete}
            >
              Delete batch
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
