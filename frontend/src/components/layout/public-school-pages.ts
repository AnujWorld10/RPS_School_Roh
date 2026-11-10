const aboutPages = [
  { label: 'About RPS', path: '/school/about/about-rps' },
  { label: "Chairman's Message", path: '/school/about/chairmans-message' },
  { label: "Principal's Message", path: '/school/about/principals-message' },
  { label: 'Vision & Mission', path: '/school/about/vision-mission' },
  { label: 'Infrastructure', path: '/school/about/infrastructure' },
  { label: 'Teachers', path: '/school/about/teachers' },
]

const academicPages = [
  { label: 'Primary (Class I–V)', path: '/school/academics/primary' },
  { label: 'Middle School (Class VI–VIII)', path: '/school/academics/middle' },
  { label: 'Secondary (Class IX–X)', path: '/school/academics/secondary' },
  { label: 'Senior Secondary (Class XI–XII)', path: '/school/academics/senior' },
]

export const publicSchoolPages = {
  '/school/home': 'Home',
  ...Object.fromEntries(aboutPages.map(({ label, path }) => [path, label])),
  ...Object.fromEntries(academicPages.map(({ label, path }) => [path, label])),
  '/school/gallery': 'Gallery',
  '/school/notices': 'Notices',
  '/school/events': 'Events',
  '/school/careers': 'Careers',
  '/school/contact': 'Contact',
} as const

export { aboutPages, academicPages }
