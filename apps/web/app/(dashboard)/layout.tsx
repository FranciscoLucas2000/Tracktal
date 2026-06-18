import LogoutButton from '@/components/auth/LogoutButton'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">
      <aside className="flex w-64 shrink-0 flex-col border-r bg-muted/20 p-4">
        <div className="flex-1" />
        <LogoutButton />
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  )
}
