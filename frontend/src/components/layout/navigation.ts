import {
  BookOpen,
  CalendarCheck,
  CalendarDays,
  ClipboardList,
  FileStack,
  FileCheck2,
  GraduationCap,
  LayoutDashboard,
  School,
  Users,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

export type NavigationItem = {
  label: string
  path: string
  icon: LucideIcon
  anyPermission?: string[]
  allPermissions?: string[]
  anyRole?: string[]
}

export type NavigationGroup = {
  label: string
  items: NavigationItem[]
}

export const navigationGroups: NavigationGroup[] = [
  {
    label: 'Overview',
    items: [{ label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard }],
  },
  {
    label: 'My portal',
    items: [
      { label: 'Student portal', path: '/portal/student', icon: GraduationCap, anyPermission: ['assignments.read'], anyRole: ['STUDENT'] },
      { label: 'Parent portal', path: '/portal/parent', icon: Users, anyPermission: ['assignments.read'], anyRole: ['PARENT'] },
      {
        label: 'Teacher workspace',
        path: '/portal/teacher',
        icon: FileStack,
        anyPermission: ['assignments.create', 'assessments.create', 'timetable.create'],
        anyRole: ['TEACHER'],
      },
    ],
  },
  {
    label: 'School',
    items: [
      { label: 'Students', path: '/students', icon: GraduationCap, anyPermission: ['students.read'] },
      { label: 'Teachers', path: '/teachers', icon: Users, anyPermission: ['teachers.read'] },
      { label: 'Classes', path: '/classes', icon: School, anyPermission: ['classes.read'] },
      { label: 'Subjects', path: '/subjects', icon: BookOpen, anyPermission: ['subjects.read'] },
      { label: 'Events', path: '/events', icon: CalendarDays, anyPermission: ['events.read'] },
    ],
  },
  {
    label: 'Admissions',
    items: [
      { label: 'Inquiries', path: '/inquiries', icon: ClipboardList, anyPermission: ['inquiries.read'] },
      {
        label: 'Interviews',
        path: '/interviews',
        icon: CalendarCheck,
        allPermissions: ['interviews.read', 'inquiries.read'],
      },
      { label: 'Applications', path: '/admissions', icon: FileCheck2, anyPermission: ['admissions.read'] },
      {
        label: 'Documents',
        path: '/documents',
        icon: FileCheck2,
        anyPermission: ['admissions.read'],
      },
    ],
  },
]

export const allNavigationItems = navigationGroups.flatMap((group) => group.items)
