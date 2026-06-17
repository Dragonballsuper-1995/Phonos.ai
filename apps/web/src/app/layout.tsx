import type { Metadata } from "next";
import { ThemeProvider } from "@/components/layout/ThemeProvider";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { PageTransition } from "@/components/layout/PageTransition";
import { SmoothScroll } from "@/components/layout/SmoothScroll";
import { CustomCursor } from "@/components/ui/CustomCursor";
import { CinematicPreloader } from "@/components/ui/CinematicPreloader";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: "PHONOS.AI | Decode Your Companion",
  description: "Intelligent, persona-based smartphone recommendation engine.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <SmoothScroll>
            <CustomCursor />
            <CinematicPreloader />
            <div className="app-container">
              <Header />
              <main className="main-content">
                <PageTransition>
                  {children}
                </PageTransition>
              </main>
              {/* <Footer /> We might remove standard footer if the page has a massive one, but keeping for mode pages */}
            </div>
          </SmoothScroll>
        </ThemeProvider>
      </body>
    </html>
  );
}
