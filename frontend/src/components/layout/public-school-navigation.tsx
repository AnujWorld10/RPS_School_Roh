import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import {
  ArrowRight,
  BellRing,
  BookOpen,
  CalendarDays,
  Clock3,
  GraduationCap,
  Images,
  Mail,
  MapPin,
  Phone,
  Search,
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/async-state'
import { rolePortalApi } from '@/features/school/role-portal-api'
import { toApiError } from '@/lib/api/api-error'
import { AboutSchoolInformation, AcademicProgrammeInformation } from './public-school-information'
import { PublicNavDropdown } from './public-nav-dropdown'
import { aboutPages, academicPages } from './public-school-pages'
import campusCelebration from '../../../images/Gemini_Generated_Image_udg88judg88judg8.jpg'
import culturalCelebration from '../../../images/Gemini_Generated_Image_leiba8leiba8leib.jpg'
import schoolCampus from '../../../images/Gemini_Generated_Image_gxwj6egxwj6egxwj.jpg'
import schoolFunction from '../../../images/Gemini_Generated_Image_exo84aexo84aexo8.jpg'

const noticeCategories = [
  'ALL',
  'GENERAL',
  'ACADEMIC',
  'EXAMINATION',
  'ADMISSION',
  'EVENT',
  'HOLIDAY',
  'CIRCULAR',
] as const

const galleryImages = [
  { src: campusCelebration, alt: 'RPS school entrance decorated for a school celebration' },
  { src: culturalCelebration, alt: 'Students in cultural dress at the school entrance' },
  { src: schoolCampus, alt: 'Students arriving at the RPS school campus' },
  { src: schoolFunction, alt: 'Students attending a school function' },
]

const schoolMapUrl = 'https://maps.app.goo.gl/TwzsvhhR1TEu3HBN6'

const frequentlyAskedQuestions = [
  'When was the school established?',
  'What is the age criteria for admission to Nursery?',
  'What is the student:teacher ratio and the total number of students in school?',
  'What is the method of teaching in the preschool?',
  'What sporting activities does the school offer?',
]

const alumniProfiles = [
  { name: 'Sample profile 01', area: 'Higher education' },
  { name: 'Sample profile 02', area: 'Community leadership' },
  { name: 'Sample profile 03', area: 'Career and innovation' },
]

const lightLinkClass =
  'whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-teal-50 hover:text-teal-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700'

const darkLinkClass =
  'whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium text-white/90 transition-colors hover:bg-white/10 hover:text-amber-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300'

export function PublicSchoolNavigation({
  variant = 'light',
  showInquiryMenu = true,
}: {
  variant?: 'light' | 'dark'
  showInquiryMenu?: boolean
}) {
  const linkClass = variant === 'dark' ? darkLinkClass : lightLinkClass
  const activeClass =
    variant === 'dark'
      ? 'bg-amber-300 font-semibold text-slate-950 hover:bg-amber-200 hover:text-slate-950'
      : 'bg-teal-50 font-semibold text-teal-900'
  const dropdownTriggerClass =
    variant === 'dark'
      ? 'text-white/90 hover:bg-white/10 hover:text-amber-100'
      : 'text-slate-700 hover:bg-teal-50 hover:text-teal-950'
  const activeLinkClass = ({ isActive }: { isActive: boolean }) => `${linkClass} ${isActive ? activeClass : ''}`

  return (
    <nav
      aria-label="School website"
      className="flex min-w-0 flex-wrap items-center gap-1 py-1"
    >
      <NavLink className={activeLinkClass} end to="/school/home">Home</NavLink>
      <PublicNavDropdown
        items={aboutPages.map(({ label, path }) => ({ label, to: path }))}
        label="About"
        triggerClassName={dropdownTriggerClass}
      />
      <PublicNavDropdown
        items={academicPages.map(({ label, path }) => ({ label, to: path }))}
        label="Academics"
        triggerClassName={dropdownTriggerClass}
      />
      {showInquiryMenu ? (
        <PublicNavDropdown
          items={[
            { label: 'New inquiry', to: '/apply' },
            { label: 'Check inquiry status', to: '/application/status' },
            { label: 'Update inquiry details', to: '/application/update' },
          ]}
          label="Inquiry"
          triggerClassName={dropdownTriggerClass}
        />
      ) : null}
      <NavLink className={activeLinkClass} to="/school/gallery">Gallery</NavLink>
      <NavLink className={activeLinkClass} to="/school/notices">Notices</NavLink>
      <NavLink className={activeLinkClass} to="/school/events">Events</NavLink>
      <NavLink className={activeLinkClass} to="/school/careers">Careers</NavLink>
      <NavLink className={activeLinkClass} to="/school/contact">Contact</NavLink>
    </nav>
  )
}

export function PublicSchoolPage({ title }: { title: string }) {
  const [noticeCategory, setNoticeCategory] = useState<(typeof noticeCategories)[number]>('ALL')
  const [noticeSearch, setNoticeSearch] = useState('')
  const noticeCount = 0
  const visibleNoticeCount = 0

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-amber-300/30 bg-gradient-to-r from-slate-950 via-teal-950 to-slate-950 text-white shadow-lg shadow-slate-950/10">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-3 sm:px-6 sm:py-4">
          <div className="flex items-center justify-between gap-4">
            <Link
              className="group flex min-w-0 items-center gap-3 rounded-lg focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-amber-300"
              to="/school/home"
            >
              <span className="flex size-11 shrink-0 items-center justify-center rounded-xl border border-amber-200/30 bg-amber-300 text-slate-950 shadow-md shadow-black/20 transition-transform group-hover:scale-105 sm:size-12">
                <GraduationCap aria-hidden="true" className="size-6 sm:size-7" />
              </span>
              <span className="min-w-0">
                <span className="block truncate text-xl font-bold tracking-tight text-white sm:text-2xl">RPS School Roh</span>
                <span className="mt-0.5 block text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-teal-100/80 sm:text-xs">
                  School website
                </span>
              </span>
            </Link>
            <PublicNavDropdown
              align="right"
              items={[
                { label: 'Student Login', to: '/login?portal=student' },
                { label: 'Sign up as a New Student', to: '/student/register' },
                { label: 'Parent Login', to: '/login?portal=parent' },
                { label: 'Teacher Login', to: '/login?portal=teacher' },
                { label: 'Administration Login', to: '/login?portal=administration' },
                { label: 'Staff Login', to: '/login' },
              ]}
              label="Sign in"
              triggerClassName="border border-white/20 bg-white/5 text-sm font-semibold text-white hover:border-amber-200/50 hover:bg-white/10 hover:text-amber-100"
            />
          </div>
          <PublicSchoolNavigation variant="dark" />
        </div>
      </header>
      <main className={title === 'Home' ? 'w-full' : 'mx-auto grid min-h-[55vh] w-full max-w-6xl content-center gap-5 px-4 py-10 sm:px-6'}>
        {title === 'Home' ? <PublicHomePage /> : title === 'Contact' ? <DemoContactPage /> : title === 'Events' ? <PublicEventsPage /> : title === 'Notices' ? (
          <section aria-labelledby="school-page-title" className="w-full">
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-teal-950 to-slate-900 px-6 py-10 text-white shadow-xl shadow-slate-900/15 sm:px-10 sm:py-12">
              <div aria-hidden="true" className="absolute -right-10 -top-20 size-64 rounded-full border border-white/10" />
              <div aria-hidden="true" className="absolute -right-2 -top-12 size-48 rounded-full border border-white/10" />
              <div className="relative max-w-3xl">
                <p className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-teal-100">
                  <BellRing aria-hidden="true" className="size-4" />
                  Notice Board
                </p>
                <h1 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl" id="school-page-title">
                  School Notices
                </h1>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-200 sm:text-base">
                  Stay updated with the latest announcements, circulars and academic notices from RPS School.
                </p>
              </div>
            </div>

            <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
              <label className="flex min-h-11 items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 focus-within:border-teal-500 focus-within:ring-2 focus-within:ring-teal-500/20">
                <Search aria-hidden="true" className="size-4 shrink-0 text-slate-500" />
                <span className="sr-only">Search notices</span>
                <input
                  className="min-w-0 flex-1 bg-transparent text-sm text-slate-900 outline-none placeholder:text-slate-500"
                  onChange={(event) => setNoticeSearch(event.target.value)}
                  placeholder="Search notices..."
                  type="search"
                  value={noticeSearch}
                />
              </label>
              <div aria-label="Filter notices by category" className="mt-4 flex gap-2 overflow-x-auto pb-1" role="group">
                {noticeCategories.map((category) => (
                  <button
                    aria-pressed={noticeCategory === category}
                    className={`min-h-9 shrink-0 rounded-full border px-4 text-xs font-semibold tracking-wide transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 ${
                      noticeCategory === category
                        ? 'border-teal-800 bg-teal-800 text-white'
                        : 'border-slate-200 bg-white text-slate-600 hover:border-teal-300 hover:bg-teal-50 hover:text-teal-900'
                    }`}
                    key={category}
                    onClick={() => setNoticeCategory(category)}
                    type="button"
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>

            <div aria-live="polite" className="mt-6">
              {visibleNoticeCount === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center">
                  <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-teal-50 text-teal-800">
                    <BellRing aria-hidden="true" className="size-6" />
                  </span>
                  <h2 className="mt-4 text-lg font-semibold text-slate-900">
                    {noticeSearch || noticeCategory !== 'ALL' ? 'No matching notices' : 'No notices published yet'}
                  </h2>
                  <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-600">
                    {noticeSearch || noticeCategory !== 'ALL'
                      ? 'Try another search term or choose a different category.'
                      : 'Official school announcements and circulars will appear here when they are published.'}
                  </p>
                </div>
              ) : null}
              <p className="mt-4 text-center text-xs text-slate-500">
                Showing {visibleNoticeCount} of {noticeCount} notices
              </p>
            </div>
          </section>
        ) : title === 'Gallery' ? (
          <section aria-labelledby="school-page-title" className="w-full">
            <p className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">
              <Images aria-hidden="true" className="size-4" />
              Moments at RPS
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950" id="school-page-title">School Gallery</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
              A glimpse of campus life and school celebrations.
            </p>
            <div className="mt-7 grid gap-4 sm:grid-cols-2">
              {galleryImages.map((image, index) => (
                <figure className="group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-md shadow-slate-900/5" key={image.src}>
                  <img
                    alt={image.alt}
                    className="aspect-[16/10] w-full object-cover transition-transform duration-300 group-hover:scale-[1.02]"
                    loading={index > 1 ? 'lazy' : 'eager'}
                    src={image.src}
                  />
                </figure>
              ))}
            </div>
            <p className="mt-4 text-xs text-slate-500">School images provided for the RPS website.</p>
          </section>
        ) : aboutPages.some(({ label }) => label === title) ? (
          <AboutSchoolInformation title={title} />
        ) : academicPages.some(({ label }) => label === title) ? (
          <AcademicProgrammeInformation title={title} />
        ) : (
          <section aria-labelledby="school-page-title" className="max-w-3xl rounded-2xl border border-teal-100 bg-white p-8 shadow-lg shadow-slate-900/5">
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">RPS School</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950" id="school-page-title">
              {title}
            </h1>
            <p className="mt-4 text-base leading-7 text-slate-600">
              Verified school information for this section has not been added yet.
            </p>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              Please check back later or contact the school office for current information.
            </p>
            <Link
              className="mt-6 inline-flex min-h-10 items-center rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground shadow-sm shadow-teal-900/20 transition-colors hover:bg-primary/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
              to="/apply"
            >
              Start an admission inquiry
            </Link>
          </section>
        )}
      </main>
      <footer className="border-t border-border bg-white px-4 py-5 text-center text-xs text-muted-foreground">
        RPS School
      </footer>
    </div>
  )
}

function PublicHomePage() {
  return (
    <>
      <section className="relative isolate flex min-h-[560px] items-center overflow-hidden bg-slate-950 sm:min-h-[640px]">
        <img
          alt=""
          aria-hidden="true"
          className="absolute inset-0 -z-20 size-full object-cover object-center"
          fetchPriority="high"
          src={campusCelebration}
        />
        <div aria-hidden="true" className="absolute inset-0 -z-10 bg-gradient-to-r from-slate-950/95 via-slate-950/75 to-slate-950/20" />
        <div className="mx-auto w-full max-w-6xl px-5 py-20 sm:px-8 lg:px-10">
          <div className="max-w-3xl text-white">
            <p className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-amber-200 backdrop-blur-sm">
              RPS School Roh
            </p>
            <h1 className="mt-6 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
              Welcome to RPS School
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-200 sm:text-lg sm:leading-8">
              A welcoming school community where students are encouraged to learn, discover their strengths, and prepare for the future.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                className="inline-flex min-h-12 items-center gap-2 rounded-lg bg-amber-400 px-5 text-sm font-semibold text-slate-950 shadow-lg shadow-black/20 transition-colors hover:bg-amber-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-200"
                to="/apply"
              >
                Start an inquiry <ArrowRight aria-hidden="true" className="size-4" />
              </Link>
              <a
                className="inline-flex min-h-12 items-center rounded-lg border border-white/35 bg-white/10 px-5 text-sm font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/20 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
                href="#about-rps"
              >
                Explore our school
              </a>
            </div>
          </div>
        </div>
        <div aria-hidden="true" className="absolute bottom-0 left-0 h-1.5 w-full bg-gradient-to-r from-amber-400 via-teal-400 to-sky-400" />
      </section>

      <section className="bg-white px-5 py-16 sm:px-8 sm:py-20" id="about-rps">
        <div className="mx-auto grid max-w-6xl items-center gap-9 md:grid-cols-2 md:gap-14">
          <div className="overflow-hidden rounded-3xl shadow-xl shadow-slate-900/10">
            <img
              alt="Students taking part in a cultural celebration at RPS School"
              className="aspect-[4/3] w-full object-cover"
              loading="lazy"
              src={culturalCelebration}
            />
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">Welcome to RPS</p>
            <h2 className="mt-3 text-3xl font-semibold leading-tight tracking-tight text-slate-950 sm:text-4xl">
              Learning, growth, and a sense of belonging
            </h2>
            <p className="mt-4 text-base leading-7 text-slate-600">
              Discover the people, learning opportunities, and school life that make RPS School a place to grow.
            </p>
            <Link
              className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-lg border border-teal-800 px-4 text-sm font-semibold text-teal-900 transition-colors hover:bg-teal-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
              to="/school/about/about-rps"
            >
              Discover RPS <ArrowRight aria-hidden="true" className="size-4" />
            </Link>
          </div>
        </div>
      </section>

      <section className="bg-slate-50 px-5 py-16 sm:px-8 sm:py-20">
        <div className="mx-auto max-w-6xl">
          <div className="max-w-3xl">
            <p className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">
              <BookOpen aria-hidden="true" className="size-4" />
              Academic programmes
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">A pathway for every stage</h2>
            <p className="mt-3 text-base leading-7 text-slate-600">
              Explore the school’s academic stages. Subject and programme details will be published as verified school information becomes available.
            </p>
          </div>
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {academicPages.map(({ label, path }, index) => (
              <Link
                className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:-translate-y-1 hover:border-teal-300 hover:shadow-lg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 sm:p-7"
                key={path}
                to={path}
              >
                <span aria-hidden="true" className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-teal-700 to-amber-400" />
                <div className="flex items-start justify-between gap-4">
                  <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-teal-50 text-sm font-bold text-teal-900">
                    {['01', '02', '03', '04'][index]}
                  </span>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                    {label.match(/\(.*\)/)?.[0].replace(/[()]/g, '')}
                  </span>
                </div>
                <h3 className="mt-5 text-lg font-semibold text-slate-950">{label.replace(/\s\(.*\)/, '')}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  School-approved subjects, activities, and learning details for this stage will be added here.
                </p>
                <span className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-teal-800">
                  Explore this stage <ArrowRight aria-hidden="true" className="size-4 transition-transform group-hover:translate-x-1" />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 py-16 sm:px-8 sm:py-20">
        <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-2">
          <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.14em] text-teal-700">
                  <BellRing aria-hidden="true" className="size-4" /> Latest notices
                </p>
                <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-950">Stay informed</h2>
              </div>
              <Link className="inline-flex min-h-10 shrink-0 items-center gap-1 text-sm font-semibold text-teal-800 hover:text-teal-950" to="/school/notices">
                All notices <ArrowRight aria-hidden="true" className="size-4" />
              </Link>
            </div>
            <p className="mt-6 rounded-xl bg-slate-50 px-4 py-5 text-sm leading-6 text-slate-600">
              No notices published yet. School announcements will appear here when available.
            </p>
          </article>
          <HomeEvents />
        </div>
      </section>

      <section className="bg-slate-950 px-5 py-16 text-white sm:px-8 sm:py-20">
        <div className="mx-auto max-w-6xl">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.16em] text-amber-300">
                <Images aria-hidden="true" className="size-4" /> Campus gallery
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Life at RPS</h2>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
                A few glimpses of campus life and school celebrations.
              </p>
            </div>
            <Link className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-white/30 px-4 text-sm font-semibold text-white transition-colors hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white" to="/school/gallery">
              View gallery <ArrowRight aria-hidden="true" className="size-4" />
            </Link>
          </div>
          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            {galleryImages.slice(0, 3).map((image) => (
              <Link className="group overflow-hidden rounded-2xl focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300" key={image.src} to="/school/gallery">
                <img
                  alt={image.alt}
                  className="aspect-[4/3] w-full object-cover transition-transform duration-300 group-hover:scale-105"
                  loading="lazy"
                  src={image.src}
                />
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section aria-labelledby="school-faq-title" className="bg-white px-5 py-16 sm:px-8 sm:py-20">
        <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">Helpful information</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl" id="school-faq-title">
              Frequently Asked Questions
            </h2>
            <p className="mt-3 max-w-lg text-sm leading-6 text-slate-600">
              We are confirming these school-specific details before publishing answers. Please contact the school office for current information.
            </p>
            <Link
              className="mt-5 inline-flex min-h-10 items-center gap-2 text-sm font-semibold text-teal-800 hover:text-teal-950"
              to="/school/contact"
            >
              Contact the school <ArrowRight aria-hidden="true" className="size-4" />
            </Link>
          </div>
          <div className="divide-y divide-slate-200 rounded-2xl border border-slate-200 bg-slate-50 px-5 sm:px-6">
            {frequentlyAskedQuestions.map((question) => (
              <details className="group py-4" key={question}>
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-left text-sm font-semibold text-slate-900 marker:content-none focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-700 sm:text-base">
                  {question}
                  <span aria-hidden="true" className="shrink-0 text-xl font-normal text-teal-800 transition-transform group-open:rotate-45">+</span>
                </summary>
                <p className="mt-3 max-w-2xl pr-8 text-sm leading-6 text-slate-600">
                  This information is being confirmed by the school. Please contact the office for the latest details.
                </p>
              </details>
            ))}
          </div>
        </div>
      </section>

      <section aria-labelledby="school-location-title" className="bg-teal-50 px-5 py-14 sm:px-8">
        <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-5 rounded-3xl border border-teal-100 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:p-8">
          <div className="flex items-start gap-4">
            <span className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-teal-100 text-teal-900">
              <MapPin aria-hidden="true" size={23} />
            </span>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-teal-800">Visit RPS</p>
              <h2 className="mt-1 text-xl font-semibold text-slate-950" id="school-location-title">Find our school</h2>
              <p className="mt-1 text-sm leading-6 text-slate-600">View the school location and get directions in Google Maps.</p>
            </div>
          </div>
          <a
            className="inline-flex min-h-11 shrink-0 items-center gap-2 rounded-lg bg-teal-900 px-4 text-sm font-semibold text-white transition-colors hover:bg-teal-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
            href={schoolMapUrl}
            rel="noopener noreferrer"
            target="_blank"
          >
            Open directions <ArrowRight aria-hidden="true" className="size-4" />
          </a>
        </div>
      </section>

      <section className="bg-gradient-to-r from-teal-900 to-slate-900 px-5 py-14 text-white sm:px-8">
        <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-5 sm:flex-row sm:items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-teal-200">Admissions</p>
            <h2 className="mt-2 text-2xl font-semibold sm:text-3xl">Take the first step with RPS School</h2>
            <p className="mt-2 text-sm leading-6 text-slate-200">Send an inquiry to begin the admission conversation.</p>
          </div>
          <Link className="inline-flex min-h-12 shrink-0 items-center gap-2 rounded-lg bg-amber-400 px-5 text-sm font-semibold text-slate-950 transition-colors hover:bg-amber-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-200" to="/apply">
            Start an inquiry <ArrowRight aria-hidden="true" className="size-4" />
          </Link>
        </div>
      </section>

      <section aria-labelledby="school-alumni-title" className="bg-slate-50 px-5 py-16 sm:px-8 sm:py-20">
        <div className="mx-auto max-w-6xl">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">Our community</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl" id="school-alumni-title">
              Our Alumni
            </h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Celebrating the journeys and achievements of the RPS community. These sample profiles are placeholders for verified alumni stories.
            </p>
          </div>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {alumniProfiles.map(({ name, area }, index) => (
              <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm" key={name}>
                <div className="flex size-12 items-center justify-center rounded-full bg-teal-900 text-sm font-bold text-amber-200">
                  {String(index + 1).padStart(2, '0')}
                </div>
                <p className="mt-5 text-xs font-semibold uppercase tracking-[0.14em] text-teal-700">Sample profile</p>
                <h3 className="mt-1 text-lg font-semibold text-slate-950">{name}</h3>
                <p className="mt-2 text-sm font-medium text-slate-600">{area}</p>
                <p className="mt-3 text-sm leading-6 text-slate-500">
                  Add a verified graduate name, year, and approved story here.
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}

function HomeEvents() {
  const events = useQuery({
    queryKey: ['public-school', 'events'],
    queryFn: rolePortalApi.publicEvents,
    retry: false,
  })
  const schoolEvents = events.data?.slice(0, 2)

  return (
    <article className="rounded-3xl border border-teal-100 bg-teal-50/60 p-6 shadow-sm sm:p-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.14em] text-teal-800">
            <CalendarDays aria-hidden="true" className="size-4" /> School calendar
          </p>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-950">School events</h2>
        </div>
        <Link className="inline-flex min-h-10 shrink-0 items-center gap-1 text-sm font-semibold text-teal-800 hover:text-teal-950" to="/school/events">
          Calendar <ArrowRight aria-hidden="true" className="size-4" />
        </Link>
      </div>
      <div className="mt-6">
        {events.isPending ? <LoadingState label="Loading upcoming events" /> : null}
        {events.error ? <ErrorState description={toApiError(events.error).message} onRetry={() => void events.refetch()} title="Events unavailable" /> : null}
        {schoolEvents?.length === 0 ? <p className="rounded-xl bg-white/80 px-4 py-5 text-sm text-slate-600">No public events published.</p> : null}
        <div className="grid gap-3">
          {schoolEvents?.map((event) => (
            <article className="rounded-xl border border-teal-100 bg-white p-4" key={event.id}>
              <p className="text-xs font-semibold text-teal-800">{new Date(event.starts_at).toLocaleString()}</p>
              <h3 className="mt-1 font-semibold text-slate-950">{event.title}</h3>
              <p className="mt-1 line-clamp-2 text-sm leading-6 text-slate-600">{event.description}</p>
            </article>
          ))}
        </div>
      </div>
    </article>
  )
}

function PublicEventsPage() {
  const events = useQuery({
    queryKey: ['public-school', 'events'],
    queryFn: rolePortalApi.publicEvents,
    retry: false,
  })

  return (
    <section aria-labelledby="school-page-title" className="w-full">
      <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">School calendar</p>
      <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950" id="school-page-title">Events</h1>
      <p className="mt-3 text-sm leading-6 text-slate-600">Public events are posted after school review.</p>
      <div className="mt-6">
        {events.isPending ? <LoadingState label="Loading public events" /> : null}
        {events.error ? <ErrorState description={toApiError(events.error).message} onRetry={() => void events.refetch()} title="Events unavailable" /> : null}
        {events.data?.length === 0 ? <EmptyState title="No public events yet" description="Approved public school events will appear here." /> : null}
        <div className="grid gap-4 md:grid-cols-2">
          {events.data?.map((event) => (
            <article className="rounded-2xl border border-teal-100 bg-white p-6 shadow-lg shadow-slate-900/5" key={event.id}>
              <p className="text-xs font-semibold uppercase tracking-wide text-teal-800">{new Date(event.starts_at).toLocaleString()}</p>
              <h2 className="mt-2 text-xl font-semibold text-slate-950">{event.title}</h2>
              <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-600">{event.description}</p>
              {event.venue ? <p className="mt-3 text-sm font-medium text-slate-700">Venue: {event.venue}</p> : null}
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}

function DemoContactPage() {
  const contactItems = [
    { icon: MapPin, label: 'Visit the school', value: 'Use the Google Maps directions to find the campus.' },
    { icon: Phone, label: 'Call the office', value: '+91 8982559219' },
    { icon: Mail, label: 'Email the office', value: 'anujworld.kumar10@gmail.com' },
    { icon: Clock3, label: 'Office hours', value: 'Monday–Saturday · 8:00 AM–2:00 PM' },
  ]

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(18rem,0.9fr)]">
      <section aria-labelledby="school-page-title" className="rounded-2xl border border-teal-100 bg-white p-6 shadow-lg shadow-slate-900/5 sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">Get in touch</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950" id="school-page-title">
          Contact RPS School
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
          For admissions, school information, or general enquiries, contact the school office during business hours.
        </p>
        <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-950">
          Demo content only — the address, phone number, email, and office hours below are placeholders. Replace them with verified school details before publishing.
        </div>
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {contactItems.map(({ icon: Icon, label, value }) => (
            <article className="rounded-xl border border-border bg-background p-4" key={label}>
              <span className="flex size-9 items-center justify-center rounded-lg bg-teal-100 text-teal-900">
                <Icon aria-hidden="true" size={18} />
              </span>
              <h2 className="mt-3 text-sm font-semibold text-slate-900">{label}</h2>
              <p className="mt-1 break-words text-sm leading-6 text-slate-600">{value}</p>
            </article>
          ))}
        </div>
      </section>
      <aside className="grid content-start gap-4">
        <section aria-labelledby="location-heading" className="rounded-2xl border border-teal-100 bg-white p-6 shadow-lg shadow-slate-900/5">
          <h2 className="text-lg font-semibold text-slate-950" id="location-heading">Find our campus</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">Open the school location in Google Maps for directions.</p>
          <a
            className="mt-4 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-teal-900 px-4 text-sm font-semibold text-white transition-colors hover:bg-teal-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
            href={schoolMapUrl}
            rel="noopener noreferrer"
            target="_blank"
          >
            <MapPin aria-hidden="true" size={17} /> View location
          </a>
        </section>
        <section className="rounded-2xl bg-slate-900 p-6 text-white shadow-lg shadow-slate-900/10">
          <h2 className="text-lg font-semibold">Admissions enquiry</h2>
          <p className="mt-2 text-sm leading-6 text-slate-300">You can start an admission inquiry online. It does not require a school staff account.</p>
          <Link className="mt-4 inline-flex min-h-10 items-center rounded-lg bg-amber-400 px-4 text-sm font-semibold text-slate-950 hover:bg-amber-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300" to="/apply">
            Start an inquiry
          </Link>
        </section>
      </aside>
    </div>
  )
}
