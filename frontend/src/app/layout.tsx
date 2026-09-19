import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AquaSense | AI Water Analytics",
  description: "Cloud-Based Water Usage Anomaly Analytics and AI Conservation Advisor",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="h-screen flex bg-gray-50">
          <div className="hidden md:flex h-full w-64 flex-col fixed inset-y-0 z-50">
            <Sidebar />
          </div>
          <main className="md:pl-64 flex-1 h-full overflow-y-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
