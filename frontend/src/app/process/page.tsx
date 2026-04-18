"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { createBatch, SessionExpiredError } from "@/lib/api";
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

export default function ProcessPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [name, setName] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const target = e.target;
    if (target.files) {
      const list = Array.from(target.files).filter((f) =>
        f.name.toLowerCase().endsWith(".pdf")
      );
      setFiles(list);
    }
  }

  function addPdfFiles(fileList: FileList | null) {
    if (!fileList?.length) return;
    const pdfs = Array.from(fileList).filter((f) =>
      f.name.toLowerCase().endsWith(".pdf")
    );
    setFiles((prev) => [...prev, ...pdfs]);
  }

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    addPdfFiles(e.dataTransfer?.files ?? null);
  }

  function removeFile(index: number) {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }

  async function submit() {
    if (files.length === 0) {
      setError("Please select at least one PDF file.");
      return;
    }
    setError("");
    setUploading(true);
    try {
      const batch = await createBatch(files, name || undefined);
      router.replace(`/batches/${batch.id}`);
    } catch (e: unknown) {
      if (e instanceof SessionExpiredError) return;
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">
          Process PDFs
        </h1>
        <p className="text-sm text-muted-foreground">
          Upload one or more PDFs to generate a single compiled learning guide.
        </p>
      </div>

      <Card className="max-w-xl border border-border shadow-lg">
        <CardHeader className="space-y-1.5 px-5 pt-3">
          <CardTitle>Upload PDFs</CardTitle>
          <CardDescription>
            Select PDF files. They will be processed with OCR and summarization,
            then compiled into one PDF. You can add a batch name to identify it
            later.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 px-5 py-3">
          <div className="space-y-3">
            <label
              htmlFor="batch-name"
              className="text-sm font-medium"
            >
              Batch name (optional)
            </label>
            <Input
              id="batch-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Semester 2 - Math"
            />
          </div>

          <div className="space-y-3">
            <label
              htmlFor="pdf-files"
              className="text-sm font-medium"
            >
              PDF files
            </label>
            <input
              id="pdf-files"
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              multiple
              className="hidden"
              onChange={onFileChange}
            />
            <div
              role="button"
              tabIndex={0}
              className={`flex w-full cursor-pointer items-center justify-center rounded-md border border-dashed border-input bg-background px-4 py-8 text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${
                dragActive ? "border-primary bg-accent" : ""
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              onKeyDown={(e) =>
                e.key === "Enter" && fileInputRef.current?.click()
              }
            >
              Choose PDFs or drag and drop
            </div>
            {files.length > 0 && (
              <ul className="mt-3 space-y-2 text-sm">
                {files.map((f, i) => (
                  <li
                    key={i}
                    className="flex items-center justify-between gap-2 rounded-md bg-muted/50 px-4 py-2.5"
                  >
                    <span className="min-w-0 truncate">{f.name}</span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-sm"
                      onClick={() => removeFile(i)}
                    >
                      ×
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {error && (
            <div className="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {error}
            </div>
          )}
        </CardContent>
        <CardFooter className="px-5 pt-4 pb-3">
          <Button
            onClick={submit}
            disabled={uploading || files.length === 0}
          >
            {uploading ? "Uploading…" : "Process PDFs"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
