import { TrendingUp, DollarSign, Building2, MapPin } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

export type NavItem = {
  label: string
  shortLabel: string
  href: string
  icon: LucideIcon
}

export const navItems: NavItem[] = [
  {
    label: 'Skill Trends',
    shortLabel: 'Trends',
    href: '/dashboard/skill-trends',
    icon: TrendingUp,
  },
  {
    label: 'Salary Benchmarks',
    shortLabel: 'Salaries',
    href: '/dashboard/salary-benchmarks',
    icon: DollarSign,
  },
  {
    label: 'Company Hiring',
    shortLabel: 'Companies',
    href: '/dashboard/company-hiring',
    icon: Building2,
  },
  {
    label: 'Location Demand',
    shortLabel: 'Locations',
    href: '/dashboard/location-demand',
    icon: MapPin,
  },
]
