"use client";

import { ChangeEvent, DragEvent, useState } from "react";
import { CheckCircle2, FileSpreadsheet, Loader2, UploadCloud, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DatasetResponse, uploadDataset } from "@/lib/api";

export default function UploadPage() {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<DatasetResponse | null>(null);

  async function handleFile(file?: File) {
    if (!file) return;
    setError("");
    setResult(null);
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setError("Please choose a CSV file. XLSX support is not enabled by the current backend.");
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      setError("The file must be smaller than 50 MB.");
      return;
    }
    setIsUploading(true);
    try {
      setResult(await uploadDataset(file));
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  function onInputChange(event: ChangeEvent<HTMLInputElement>) {
    void handleFile(event.target.files?.[0]);
  }

  function onDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setIsDragging(false);
    void handleFile(event.dataTransfer.files[0]);
  }

  return (
    <div className="p-8 space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Upload Data</h2>
        <p className="text-muted-foreground mt-2">Process one water-consumption CSV and make it available across AquaSense.</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Choose a dataset</CardTitle></CardHeader>
        <CardContent>
          <label
            htmlFor="dataset-file"
            onDragOver={(event) => { event.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={onDrop}
            className={`flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition ${isDragging ? "border-blue-500 bg-blue-50" : "border-slate-200 bg-slate-50 hover:border-blue-400"}`}
          >
            {isUploading ? <Loader2 className="mb-4 h-10 w-10 animate-spin text-blue-600" /> : <UploadCloud className="mb-4 h-10 w-10 text-blue-600" />}
            <span className="font-semibold">{isUploading ? "Uploading and profiling dataset..." : "Drop a CSV here or browse"}</span>
            <span className="mt-2 text-sm text-slate-500">Required fields: a date/time column and a consumption column. Maximum 50 MB.</span>
            <input id="dataset-file" type="file" accept=".csv,text/csv" className="sr-only" onChange={onInputChange} disabled={isUploading} />
          </label>
        </CardContent>
      </Card>

      {error && <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700"><XCircle className="h-5 w-5 shrink-0" />{error}</div>}

      {result && <Card className="border-emerald-200">
        <CardHeader><CardTitle className="flex items-center gap-2"><CheckCircle2 className="h-5 w-5 text-emerald-600" />Dataset processed successfully</CardTitle></CardHeader>
        <CardContent className="space-y-5">
          <div className="flex items-center gap-3"><FileSpreadsheet className="h-8 w-8 text-blue-600" /><div><p className="font-medium">{result.dataset.filename}</p><p className="text-sm text-slate-500">Uploaded {new Date(result.dataset.created_at).toLocaleString()}</p></div></div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Metric label="Rows" value={result.dataset.profile.rows.toLocaleString()} />
            <Metric label="Columns" value={result.dataset.profile.columns.toLocaleString()} />
            <Metric label="Missing values" value={result.dataset.profile.missing_values.toLocaleString()} />
            <Metric label="Quality score" value={`${result.dataset.profile.quality_score}%`} />
          </div>
          <div className="grid gap-2 text-sm text-slate-600 sm:grid-cols-2"><p><strong>Timestamp:</strong> {result.dataset.profile.timestamp_column}</p><p><strong>Consumption:</strong> {result.dataset.profile.consumption_column}</p><p><strong>Duplicates found:</strong> {result.dataset.profile.duplicates}</p><p><strong>Rows cleaned:</strong> {result.dataset.cleaning.removed_rows}</p></div>
          <p className="text-sm text-emerald-700">The same stored dataset is now used by Dashboard, Analytics, Anomalies, Forecast, AI Analyst, and Reports.</p>
        </CardContent>
      </Card>}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg bg-slate-50 p-4"><p className="text-xs uppercase tracking-wide text-slate-500">{label}</p><p className="mt-1 text-xl font-semibold">{value}</p></div>;
}
