"use client";

import { useEffect, useState } from "react";
import { BarChart3, Loader2 } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getAnalytics } from "@/lib/api";

type AnalyticsData = { overview: { basic_statistics: Record<string, number>; peak_analysis: Record<string, string | number> }; daily: Record<string, string | number>[]; monthly: Record<string, string | number>[] };

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { getAnalytics().then((value) => setData(value as unknown as AnalyticsData)).catch((value) => setError(value instanceof Error ? value.message : "Analytics could not be loaded.")); }, []);
  if (error) return <State title="Analytics unavailable" message={error} />;
  if (!data) return <Loading label="Loading analytics..." />;
  const stats = data.overview.basic_statistics;
  const dailyKey = Object.keys(data.daily[0] ?? {}).find((key) => key !== "date" && key !== "timestamp") ?? "consumption";
  const dateKey = Object.keys(data.daily[0] ?? {}).find((key) => key !== dailyKey) ?? "timestamp";
  return <div className="space-y-8 p-8"><header><h2 className="text-3xl font-bold tracking-tight">Analytics</h2><p className="mt-2 text-slate-500">Statistical analysis from the currently uploaded dataset.</p></header><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">{[["Total consumption", stats.total_consumption], ["Average", stats.average_consumption], ["Median", stats.median_consumption], ["Minimum", stats.minimum_consumption], ["Maximum", stats.maximum_consumption]].map(([label, value]) => <Card key={label as string}><CardContent className="p-5"><p className="text-sm text-slate-500">{label}</p><p className="mt-2 text-2xl font-bold">{Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 })}</p></CardContent></Card>)}</div><div className="grid gap-6 lg:grid-cols-2"><ChartCard title="Daily consumption"><ResponsiveContainer width="100%" height="100%"><LineChart data={data.daily}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey={dateKey} hide /><YAxis /><Tooltip /><Line type="monotone" dataKey={dailyKey} stroke="#2563eb" strokeWidth={3} dot={false} /></LineChart></ResponsiveContainer></ChartCard><ChartCard title="Monthly consumption"><ResponsiveContainer width="100%" height="100%"><BarChart data={data.monthly}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey={dateKey} hide /><YAxis /><Tooltip /><Bar dataKey={dailyKey} fill="#8b5cf6" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></ChartCard></div><Card><CardHeader><CardTitle>Peak and low usage</CardTitle></CardHeader><CardContent className="grid gap-3 sm:grid-cols-2"><p>Peak: <strong>{String(data.overview.peak_analysis.peak_consumption)}</strong> at {String(data.overview.peak_analysis.peak_timestamp)}</p><p>Lowest: <strong>{String(data.overview.peak_analysis.lowest_consumption)}</strong> at {String(data.overview.peak_analysis.lowest_timestamp)}</p></CardContent></Card></div>;
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) { return <Card><CardHeader><CardTitle>{title}</CardTitle></CardHeader><CardContent><div className="h-72">{children}</div></CardContent></Card>; }
function Loading({ label }: { label: string }) { return <div className="flex min-h-96 items-center justify-center gap-3 p-8 text-slate-500"><Loader2 className="h-5 w-5 animate-spin" />{label}</div>; }
function State({ title, message }: { title: string; message: string }) { return <div className="m-8 rounded-xl border border-amber-200 bg-amber-50 p-8"><BarChart3 className="mb-3 h-8 w-8 text-amber-600" /><h2 className="text-xl font-semibold">{title}</h2><p className="mt-2 text-slate-600">{message}</p></div>; }