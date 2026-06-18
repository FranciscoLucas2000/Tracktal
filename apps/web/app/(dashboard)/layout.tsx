import { SidebarProvider } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/dashboard/AppSidebar'
import { TopBar } from '@/components/dashboard/TopBar'
import { BottomNav } from '@/components/dashboard/BottomNav'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <div className="flex min-h-screen flex-1 flex-col">
        <TopBar />
        <main className="flex-1 p-6 pb-20 md:pb-6">{children}</main>
        <BottomNav />
      </div>
    </SidebarProvider>
  )
}
