import { ArrowRight, BookOpen, CheckCircle2, GraduationCap, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'
import { academicPages } from './public-school-pages'

type AboutPageContent = {
  eyebrow: string
  introduction: string
  paragraphs: string[]
  highlights: { title: string; description: string }[]
}

const aboutPageContent: Record<string, AboutPageContent> = {
  'About RPS': {
    eyebrow: 'A place to learn and grow',
    introduction: 'An encouraging school community where every learner is supported to discover their strengths and take the next step with confidence.',
    paragraphs: [
      'At RPS School, education is about more than completing a syllabus. It is an opportunity to build curiosity, character, confidence, and a lasting respect for learning.',
      'We aim to create a welcoming environment where students are encouraged to ask questions, learn with others, and make steady progress. Families and educators share an important role in helping each child feel supported.',
    ],
    highlights: [
      { title: 'Learning with purpose', description: 'Build understanding, ask thoughtful questions, and connect learning to everyday life.' },
      { title: 'Character and care', description: 'Practice respect, responsibility, kindness, and consideration for others.' },
      { title: 'Growing together', description: 'Recognize each learner’s progress and encourage them to take on new challenges.' },
    ],
  },
  "Chairman's Message": {
    eyebrow: 'A message from our leadership',
    introduction: 'Every child deserves the opportunity to learn in an environment that values effort, integrity, and possibility.',
    paragraphs: [
      'At RPS School, our shared responsibility is to help young people grow into thoughtful, capable, and compassionate individuals. We want every student to feel encouraged to explore their interests, develop strong foundations, and take pride in their progress.',
      'We value the trust families place in our school. By working together with openness and care, we can create meaningful opportunities for students and prepare them to meet the future with confidence.',
    ],
    highlights: [
      { title: 'Purposeful education', description: 'Learning should prepare students to think clearly, act responsibly, and contribute positively.' },
      { title: 'A shared partnership', description: 'Families, educators, and students make the strongest progress when they work together.' },
      { title: 'A bright future', description: 'We remain committed to building a school community in which every learner can thrive.' },
    ],
  },
  "Principal's Message": {
    eyebrow: 'A message from our Principal',
    introduction: 'A strong school experience brings together engaging learning, consistent encouragement, and a sense of belonging.',
    paragraphs: [
      'We want our students to come to school ready to wonder, participate, and try. In every stage of learning, patient guidance and meaningful feedback can help children become more confident and independent.',
      'We encourage our students to value their own effort and the contributions of others. With the support of families and teachers, each learner can develop the knowledge, habits, and consideration that will serve them well beyond the classroom.',
    ],
    highlights: [
      { title: 'Curiosity in the classroom', description: 'Invite students to ask questions, discuss ideas, and take an active part in learning.' },
      { title: 'Progress for every learner', description: 'Notice individual strengths and offer encouragement as students work through challenges.' },
      { title: 'Respect and responsibility', description: 'Create a caring culture where students learn to listen, cooperate, and contribute.' },
    ],
  },
  'Vision & Mission': {
    eyebrow: 'What guides us',
    introduction: 'Our vision and mission express the kind of learning community we aspire to build with our students and families.',
    paragraphs: [
      'Our vision is to nurture confident, compassionate, and curious learners who are ready to contribute thoughtfully to their communities.',
      'Our mission is to provide a supportive environment for meaningful learning, encourage each student to develop their abilities, and strengthen the values of respect, responsibility, and lifelong curiosity.',
    ],
    highlights: [
      { title: 'Curiosity', description: 'Encourage students to explore ideas, ask questions, and keep learning.' },
      { title: 'Integrity', description: 'Promote honesty, accountability, and thoughtful choices in school life.' },
      { title: 'Belonging', description: 'Respect every learner and create a community where people feel welcome.' },
    ],
  },
  Infrastructure: {
    eyebrow: 'Spaces that support learning',
    introduction: 'A thoughtfully planned school environment can support focused study, creativity, movement, and connection.',
    paragraphs: [
      'Our approach to the learning environment puts student wellbeing, accessibility, safety, and purposeful use of space first. We aim for spaces that are welcoming, cared for, and suited to the needs of the learners who use them.',
      'The facilities below are examples of areas families may want to learn about. Please confirm current campus facilities with the school before relying on this sample information.',
    ],
    highlights: [
      { title: 'Classrooms and learning spaces', description: 'Comfortable, organized spaces designed to support lessons, discussion, and collaborative work.' },
      { title: 'Reading and discovery', description: 'Dedicated resources and spaces that encourage reading, research, and exploration.' },
      { title: 'Activity and outdoor areas', description: 'Places for movement, recreation, and participation in school activities.' },
    ],
  },
  Teachers: {
    eyebrow: 'The people who support learning',
    introduction: 'Caring and committed educators help students feel seen, stay curious, and make progress with confidence.',
    paragraphs: [
      'Strong teaching begins with understanding learners. Clear explanations, thoughtful questions, and constructive feedback can help students build knowledge and become more independent over time.',
      'We value respectful relationships between students, teachers, and families. The principles on this page describe the approach we aspire to; please contact the school for verified staff information and current team details.',
    ],
    highlights: [
      { title: 'Supportive guidance', description: 'Encourage participation and help students approach challenges with confidence.' },
      { title: 'Thoughtful feedback', description: 'Help learners understand what they have achieved and identify their next steps.' },
      { title: 'Partnership with families', description: 'Keep communication respectful and focused on each student’s wellbeing and progress.' },
    ],
  },
}

type AcademicStage = {
  classes: string
  introduction: string
  learningGoals: { title: string; description: string }[]
  learningAreas: string[]
  experiences: string[]
}

const academicStageContent: Record<string, AcademicStage> = {
  'Primary (Class I–V)': {
    classes: 'Classes I–V',
    introduction: 'A supportive stage for building strong learning habits, exploring core ideas, and developing confidence as a young learner.',
    learningGoals: [
      { title: 'Strong foundations', description: 'Develop early confidence in reading, writing, mathematical thinking, and communication.' },
      { title: 'Curiosity and exploration', description: 'Use questions, observation, and practical activities to make sense of new ideas.' },
      { title: 'Learning together', description: 'Practice listening, sharing ideas, and working cooperatively with classmates.' },
      { title: 'Growing independence', description: 'Build organization, perseverance, and confidence in taking on new tasks.' },
    ],
    learningAreas: ['Language and literacy', 'Mathematical thinking', 'Science and discovery', 'Social understanding', 'Creative expression'],
    experiences: ['Reading and storytelling', 'Hands-on investigations', 'Creative projects', 'Group discussion and presentation'],
  },
  'Middle School (Class VI–VIII)': {
    classes: 'Classes VI–VIII',
    introduction: 'A bridge into deeper subject learning, where students strengthen core knowledge and begin to take greater ownership of their progress.',
    learningGoals: [
      { title: 'Deeper understanding', description: 'Connect ideas across subjects and explain how students arrived at an answer.' },
      { title: 'Critical thinking', description: 'Compare information, consider evidence, and develop reasoned points of view.' },
      { title: 'Independent learning', description: 'Strengthen planning, study routines, research, and responsible use of resources.' },
      { title: 'Communication and teamwork', description: 'Share ideas clearly and contribute thoughtfully to collaborative work.' },
    ],
    learningAreas: ['Languages and communication', 'Mathematics', 'Science and investigation', 'Humanities and society', 'Digital and creative learning'],
    experiences: ['Research and inquiry projects', 'Experiments and demonstrations', 'Presentations and discussion', 'Collaborative problem-solving'],
  },
  'Secondary (Class IX–X)': {
    classes: 'Classes IX–X',
    introduction: 'A focused stage for consolidating subject knowledge, strengthening analytical skills, and preparing for important academic milestones.',
    learningGoals: [
      { title: 'Subject mastery', description: 'Strengthen understanding through regular practice, revision, and application.' },
      { title: 'Analytical thinking', description: 'Interpret information, evaluate evidence, and solve increasingly complex problems.' },
      { title: 'Effective study habits', description: 'Develop realistic plans for practice, review, and preparation for assessments.' },
      { title: 'Future awareness', description: 'Reflect on interests and begin exploring possible next steps in learning.' },
    ],
    learningAreas: ['Languages and communication', 'Mathematical reasoning', 'Scientific thinking', 'Humanities and social understanding', 'Technology and applied learning'],
    experiences: ['Structured revision and practice', 'Subject-based investigations', 'Research and written assignments', 'Guidance on study planning'],
  },
  'Senior Secondary (Class XI–XII)': {
    classes: 'Classes XI–XII',
    introduction: 'A transition toward advanced study, thoughtful subject choices, and preparation for further education and future goals.',
    learningGoals: [
      { title: 'Advanced learning', description: 'Engage deeply with the subjects and pathways offered by the school.' },
      { title: 'Independent scholarship', description: 'Strengthen research, analysis, academic writing, and self-directed study.' },
      { title: 'Purposeful preparation', description: 'Build consistent routines for assessments and future-study planning.' },
      { title: 'Personal direction', description: 'Reflect on interests, strengths, and potential routes beyond school.' },
    ],
    learningAreas: ['School-approved subject pathways', 'Advanced subject study', 'Research and academic communication', 'Further-study and career exploration'],
    experiences: ['Subject-focused projects', 'Independent research and presentations', 'Assessment preparation', 'Further-study planning'],
  },
}

export function AboutSchoolInformation({ title }: { title: string }) {
  const content = aboutPageContent[title]
  if (!content) return null

  return (
    <section aria-labelledby="school-page-title" className="w-full">
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-teal-950 to-slate-900 px-6 py-9 text-white shadow-xl shadow-slate-900/15 sm:px-10 sm:py-12">
        <div aria-hidden="true" className="absolute -right-12 -top-20 size-64 rounded-full border border-white/10" />
        <div className="relative max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-amber-200">{content.eyebrow}</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl" id="school-page-title">{title}</h1>
          <p className="mt-4 text-base leading-7 text-slate-200 sm:text-lg">{content.introduction}</p>
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-950">
        Sample website content — please have the school review and approve this information before publication.
      </div>

      <div className="mt-7 grid gap-6 lg:grid-cols-[minmax(0,1.35fr)_minmax(16rem,0.65fr)]">
        <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div className="flex items-center gap-3">
            <span className="flex size-10 items-center justify-center rounded-xl bg-teal-50 text-teal-800">
              <BookOpen aria-hidden="true" size={20} />
            </span>
            <h2 className="text-xl font-semibold text-slate-950">Our approach</h2>
          </div>
          <div className="mt-5 space-y-4 text-sm leading-7 text-slate-600 sm:text-base">
            {content.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
          </div>
        </article>
        <aside className="rounded-2xl bg-teal-950 p-6 text-white shadow-sm sm:p-7">
          <span className="flex size-10 items-center justify-center rounded-xl bg-white/10 text-amber-200">
            <Sparkles aria-hidden="true" size={20} />
          </span>
          <h2 className="mt-4 text-xl font-semibold">What matters to us</h2>
          <ul className="mt-5 space-y-4">
            {content.highlights.map(({ title: highlightTitle, description }) => (
              <li className="flex items-start gap-3" key={highlightTitle}>
                <CheckCircle2 aria-hidden="true" className="mt-0.5 size-5 shrink-0 text-amber-300" />
                <span>
                  <strong className="block text-sm font-semibold">{highlightTitle}</strong>
                  <span className="mt-1 block text-sm leading-6 text-teal-100/80">{description}</span>
                </span>
              </li>
            ))}
          </ul>
        </aside>
      </div>
      <div className="mt-7 flex flex-wrap gap-3">
        <Link
          className="inline-flex min-h-11 items-center gap-2 rounded-lg bg-teal-900 px-4 text-sm font-semibold text-white transition-colors hover:bg-teal-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
          to="/apply"
        >
          Start an inquiry <ArrowRight aria-hidden="true" className="size-4" />
        </Link>
        <Link
          className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-800 transition-colors hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
          to="/school/contact"
        >
          Contact RPS School
        </Link>
      </div>
    </section>
  )
}

export function AcademicProgrammeInformation({ title }: { title: string }) {
  const stage = academicStageContent[title]
  if (!stage) return null

  return (
    <section aria-labelledby="school-page-title" className="w-full">
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-teal-950 to-slate-900 px-6 py-9 text-white shadow-xl shadow-slate-900/15 sm:px-10 sm:py-12">
        <div aria-hidden="true" className="absolute -right-12 -top-16 size-64 rounded-full border border-white/10" />
        <div className="relative max-w-3xl">
          <p className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.16em] text-amber-200">
            <GraduationCap aria-hidden="true" className="size-4" /> Academic programmes
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl" id="school-page-title">{title}</h1>
          <p className="mt-2 text-sm font-medium text-teal-100">{stage.classes}</p>
          <p className="mt-4 text-base leading-7 text-slate-200 sm:text-lg">{stage.introduction}</p>
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-950">
        Illustrative programme overview — confirm the school’s curriculum, subjects, and activities before publication.
      </div>

      <div className="mt-8">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">A strong foundation</p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">Learning goals for this stage</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            As students progress, they build knowledge, confidence, and the skills to take an active role in their learning.
          </p>
        </div>
        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          {stage.learningGoals.map(({ title: goalTitle, description }, index) => (
            <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6" key={goalTitle}>
              <span className="flex size-10 items-center justify-center rounded-xl bg-teal-50 text-sm font-bold text-teal-900">
                {String(index + 1).padStart(2, '0')}
              </span>
              <h3 className="mt-4 text-lg font-semibold text-slate-950">{goalTitle}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
            </article>
          ))}
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <article className="rounded-2xl border border-teal-100 bg-teal-50/60 p-6 sm:p-7">
          <p className="text-sm font-semibold uppercase tracking-[0.14em] text-teal-800">Areas of learning</p>
          <h2 className="mt-2 text-xl font-semibold text-slate-950">Explore, practice, understand</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            The following learning areas are illustrative; actual subject offerings should be confirmed with the school.
          </p>
          <ul className="mt-5 grid gap-2 sm:grid-cols-2">
            {stage.learningAreas.map((area) => (
              <li className="flex items-start gap-2 rounded-lg bg-white px-3 py-2.5 text-sm font-medium text-slate-700" key={area}>
                <CheckCircle2 aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-teal-700" />
                {area}
              </li>
            ))}
          </ul>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
          <p className="text-sm font-semibold uppercase tracking-[0.14em] text-teal-800">Beyond the lesson</p>
          <h2 className="mt-2 text-xl font-semibold text-slate-950">Learning through experience</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            A balanced programme can give students opportunities to apply ideas, share their thinking, and learn with others.
          </p>
          <ul className="mt-5 space-y-3">
            {stage.experiences.map((experience) => (
              <li className="flex items-start gap-3 text-sm leading-6 text-slate-700" key={experience}>
                <Sparkles aria-hidden="true" className="mt-1 size-4 shrink-0 text-amber-600" />
                {experience}
              </li>
            ))}
          </ul>
        </article>
      </div>

      <div className="mt-8 rounded-2xl bg-slate-950 p-6 text-white sm:flex sm:items-center sm:justify-between sm:gap-6 sm:p-8">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.14em] text-amber-300">Next steps</p>
          <h2 className="mt-2 text-xl font-semibold">Explore the school’s other learning stages</h2>
        </div>
        <nav aria-label="Academic stages" className="mt-4 flex flex-wrap gap-2 sm:mt-0 sm:justify-end">
          {academicPages.map(({ label, path }) => (
            <Link
              aria-current={label === title ? 'page' : undefined}
              className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300 ${
                label === title ? 'bg-amber-300 text-slate-950' : 'bg-white/10 text-white hover:bg-white/20'
              }`}
              key={path}
              to={path}
            >
              {label}
            </Link>
          ))}
        </nav>
      </div>

      <div className="mt-6">
        <Link
          className="inline-flex min-h-11 items-center gap-2 rounded-lg bg-teal-900 px-4 text-sm font-semibold text-white transition-colors hover:bg-teal-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
          to="/apply"
        >
          Ask about admissions <ArrowRight aria-hidden="true" className="size-4" />
        </Link>
      </div>
    </section>
  )
}
