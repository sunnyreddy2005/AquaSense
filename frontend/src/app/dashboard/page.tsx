"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { Activity, Droplet, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react";
import { getAnalytics } from "@/lib/api";

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { getAnalytics().then(setAnalytics).catch((value) => setError(value instanceof Error ? value.message : "No dataset available.")); }, []);
  if (error) return <div className="p-8"><h2 className="text-3xl font-bold tracking-tight">Dashboard Overview</h2><div className="mt-8 rounded-xl border border-blue-200 bg-blue-50 p-8"><h3 className="text-xl font-semibold">No water consumption data available</h3><p className="mt-2 text-slate-600">Upload a dataset to start analyzing your water consumption.</p><Link href="/upload" className="mt-5 inline-block rounded-lg bg-blue-600 px-4 py-2 font-medium text-white">Upload Data</Link></div></div>;
  if (!analytics) return <div className="p-8 text-slate-500">Loading dashboard...</div>;
  const overview = analytics.overview as { basic_statistics: Record<string, number>; peak_analysis: Record<string, string | number> };
  const stats = overview.basic_statistics;
  const peak = overview.peak_analysis;
  const consumptionData = (analytics.daily as Record<string, string | number>[]).slice(-30).map((item) => ({ time: String(item[Object.keys(item)[0]]), usage: Number(item[Object.keys(item)[1]]) }));
  const weeklyData = (analytics.weekly as Record<string, string | number>[]).slice(-7).map((item) => ({ day: String(item[Object.keys(item)[0]]), usage: Number(item[Object.keys(item)[1]]) }));
  return (
    <div className="p-8 space-y-8">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard Overview</h2>
        <div className="flex items-center space-x-2">
          {/* Mock Date Picker Area */}
          <div className="bg-white px-4 py-2 rounded-md border text-sm text-gray-500 shadow-sm">
            Last 7 Days
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Usage</CardTitle>
            <Droplet className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_consumption.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
            <p className="text-xs text-muted-foreground">From uploaded dataset</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Daily</CardTitle>
            <Activity className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.average_consumption.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
            <p className="text-xs text-muted-foreground">Average observation</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Peak Usage</CardTitle>
            <TrendingUp className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{String(peak.peak_consumption)}</div>
            <p className="text-xs text-muted-foreground">{String(peak.peak_timestamp)}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Anomalies Detected</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">See Anomalies</div>
            <p className="text-xs text-muted-foreground">Computed on demand</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Quality</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{String((analytics.profile as { quality_score: number }).quality_score)}%</div>
            <p className="text-xs text-muted-foreground">Dataset quality score</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Daily Consumption Trend</CardTitle>
          </CardHeader>
          <CardContent className="pl-2">
            <div className="h-75">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={consumptionData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee" />
                  <XAxis dataKey="time" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}L`} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  <Line type="monotone" dataKey="usage" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6' }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Weekly Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-75">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee" />
                  <XAxis dataKey="day" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  <Bar dataKey="usage" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
