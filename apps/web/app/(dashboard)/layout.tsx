export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 shrink-0 border-r bg-muted/20" />
      <main className="flex-1 p-8">{children}</main>
    </div>
  )
}
