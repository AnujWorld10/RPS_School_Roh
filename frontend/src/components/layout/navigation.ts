import {
  BookOpen,
  CalendarCheck,
  ClipboardList,
  FileCheck2,
  GraduationCap,
  LayoutDashboard,
  School,
  Users,
  Wallet,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

export type NavigationItem = {
  label: string
  path: string
  icon: LucideIcon
  anyPermission?: string[]
}

export type NavigationGroup = {
  label: string
  items: NavigationItem[]
}

export const navigationGroups: NavigationGroup[] = [
  {
    label: 'Overview',
    items: [{ label: 'Dashboard', path: '/', icon: LayoutDashboard }],
  },
  {
    label: 'School',
    items: [
      { label: 'Students', path: '/students', icon: GraduationCap, anyPermission: ['students.read'] },
      { label: 'Teachers', path: '/teachers', icon: Users, anyPermission: ['teachers.read'] },
      { label: 'Classes', path: '/classes', icon: School, anyPermission: ['classes.read'] },
      { label: 'Subjects', path: '/subjects', icon: BookOpen, anyPermission: ['subjects.read'] },
    ],
  },
  {
    label: 'Admissions',
    items: [
      { label: 'Inquiries', path: '/inquiries', icon: ClipboardList, anyPermission: ['inquiries.read'] },
      { label: 'Interviews', path: '/interviews', icon: CalendarCheck, anyPermission: ['interviews.read'] },
      { label: 'Applications', path: '/admissions', icon: FileCheck2, anyPermission: ['admissions.read'] },
      {
        label: 'Documents',
        path: '/documents',
        icon: FileCheck2,
        anyPermission: ['admissions.update', 'admissions.verify_documents'],
      },
    ],
  },
  {
    label: 'Operations',
    items: [
      {
        label: 'Teacher attendance',
        path: '/teacher-attendance',
        icon: CalendarCheck,
        anyPermission: ['teachers.update'],
      },
      {
        label: 'Salary payments',
        path: '/salary',
        icon: Wallet,
        anyPermission: ['teachers.salary.read', 'teachers.salary.pay'],
      },
    ],
  },
]

export const allNavigationItems = navigationGroups.flatMap((group) => group.items)
