"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getAnomalies } from "@/lib/api";

type Anomaly = { timestamp: string; observed_value: number; baseline: number; deviation_percent: number; severity: string; methods_detected: string[] };
type AnomalyData = { total_anomalies_detected: number; severity_counts: Record<string, number>; anomalies: Anomaly[] };

export default function AnomaliesPage() {
  const [data, setData] = useState<AnomalyData | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { getAnomalies().then((value) => setData(value as unknown as AnomalyData)).catch((value) => setError(value instanceof Error ? value.message : "Anomalies could not be loaded.")); }, []);
  if (error) return <State message={error} />;
  if (!data) return <div className="flex min-h-96 items-center justify-center gap-3 p-8 text-slate-500"><Loader2 className="h-5 w-5 animate-spin" />Detecting anomalies...</div>;
  return <div className="space-y-8 p-8"><header><h2 className="text-3xl font-bold tracking-tight">Anomalies</h2><p className="mt-2 text-slate-500">Detected with rolling baseline, z-score, and isolation forest methods.</p></header><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><Card><CardContent className="p-5"><p className="text-sm text-slate-500">Detected</p><p className="mt-2 text-3xl font-bold text-red-600">{data.total_anomalies_detected}</p></CardContent></Card>{Object.entries(data.severity_counts).map(([severity, count]) => <Card key={severity}><CardContent className="p-5"><p className="text-sm capitalize text-slate-500">{severity} severity</p><p className="mt-2 text-3xl font-bold">{count}</p></CardContent></Card>)}</div><Card><CardHeader><CardTitle>Investigate observations</CardTitle></CardHeader><CardContent><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="border-b text-slate-500"><tr><th className="p-3">Timestamp</th><th className="p-3">Observed</th><th className="p-3">Baseline</th><th className="p-3">Deviation</th><th className="p-3">Severity</th><th className="p-3">Evidence</th></tr></thead><tbody>{data.anomalies.map((anomaly) => <tr key={`${anomaly.timestamp}-${anomaly.observed_value}`} className="border-b last:border-0"><td className="p-3">{anomaly.timestamp}</td><td className="p-3 font-medium">{anomaly.observed_value}</td><td className="p-3">{anomaly.baseline}</td><td className="p-3">{anomaly.deviation_percent}%</td><td className="p-3"><span className={`rounded-full px-2 py-1 text-xs capitalize ${anomaly.severity === "high" ? "bg-red-100 text-red-700" : anomaly.severity === "medium" ? "bg-orange-100 text-orange-700" : "bg-slate-100 text-slate-700"}`}>{anomaly.severity}</span></td><td className="p-3">{anomaly.methods_detected.join(", ")}</td></tr>)}</tbody></table>{data.anomalies.length === 0 && <p className="p-6 text-center text-slate-500">No unusual observations were detected in this dataset.</p>}</div></CardContent></Card></div>;
}

function State({ message }: { message: string }) { return <div className="m-8 rounded-xl border border-amber-200 bg-amber-50 p-8"><AlertTriangle className="mb-3 h-8 w-8 text-amber-600" /><h2 className="text-xl font-semibold">Anomaly detection unavailable</h2><p className="mt-2 text-slate-600">{message}</p></div>; }