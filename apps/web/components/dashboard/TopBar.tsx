import { SidebarTrigger } from '@/components/ui/sidebar'
import { createClient } from '@/lib/supabase/server'
import { UserMenu } from './UserMenu'

export async function TopBar() {
  const supabase = createClient()
  const {
    data: { user },
  } = await supabase.auth.getUser()

  return (
    <header className="sticky top-0 z-10 flex h-14 items-center gap-4 border-b bg-background px-4">
      <SidebarTrigger className="hidden md:flex" />
      <div className="flex-1" />
      <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
        Free
      </span>
      {user && <UserMenu email={user.email ?? 'Account'} />}
    </header>
  )
}
