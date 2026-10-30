import { Suspense, lazy } from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import Home from './pages/Home'
import { usePageviews } from './lib/analytics'
import GestionDefilement from './components/GestionDefilement'

// Pages chargées à la demande (code-splitting), recharts/leaflet ne pèsent
// sur le chargement que lorsqu'on visite réellement ces pages.
const Methodologie = lazy(() => import('./pages/Methodologie'))
const About = lazy(() => import('./pages/About'))
const MentionsLegales = lazy(() => import('./pages/MentionsLegales'))
const Presse = lazy(() => import('./pages/Presse'))
const Newsletter = lazy(() => import('./pages/Newsletter'))
const Fil = lazy(() => import('./pages/Fil'))
const NotFound = lazy(() => import('./pages/NotFound'))

const Atlas = lazy(() => import('./pages/atlas/Atlas'))
const Territoires = lazy(() => import('./pages/territoire/Territoires'))
const UnitView = lazy(() => import('./pages/explorer/UnitView'))

const OutilsList = lazy(() => import('./pages/outils/OutilsList'))
const RepresentativiteTool = lazy(() => import('./pages/outils/RepresentativiteTool'))

const TerrainsList = lazy(() => import('./pages/terrains/TerrainsList'))
const TerrainElus = lazy(() => import('./pages/terrains/TerrainElus'))
const TerrainEcole = lazy(() => import('./pages/terrains/TerrainEcole'))
const TerrainAssemblee = lazy(() => import('./pages/terrains/TerrainAssemblee'))
const TerrainSelectivite = lazy(() => import('./pages/terrains/TerrainSelectivite'))
const TerrainAutoEcoles = lazy(() => import('./pages/terrains/TerrainAutoEcoles'))
const TerrainRevenus = lazy(() => import('./pages/terrains/TerrainRevenus'))
const TerrainSport = lazy(() => import('./pages/terrains/TerrainSport'))

const Segregation = lazy(() => import('./pages/segregation/Segregation'))
const International = lazy(() => import('./pages/international/International'))
const Pisa = lazy(() => import('./pages/international/Pisa'))

const ThemesList = lazy(() => import('./pages/themes/ThemesList'))
const ThemeDetail = lazy(() => import('./pages/themes/ThemeDetail'))

// Vues intégrables (iframe), rendues SANS le chrome du site (ni en-tête ni pied).
const Embed = lazy(() => import('./pages/embed/Embed'))

const Loading = () => <div className="py-20 text-center text-gray-400">Chargement…</div>

// Application normale (avec en-tête, pied, gestion d'erreur).
function MainApp() {
  usePageviews() // compte les navigations SPA (hors vues /embed)
  return (
    <Layout>
      <ErrorBoundary
        fallback={
          <div className="py-20 px-4 text-center">
            <p className="text-gray-700 font-medium mb-2">Une erreur est survenue sur cette page.</p>
            <a href="/" className="text-blue-600 hover:underline">Revenir à l'accueil</a>
          </div>
        }
      >
        <Suspense fallback={<Loading />}>
          <Routes>
            {/* Accueil */}
            <Route path="/" element={<Home />} />

            {/* Atlas */}
            <Route path="/atlas" element={<Atlas />} />

            {/* Territoires (fiche + tableau de bord national) */}
            <Route path="/territoires" element={<Territoires />} />

            {/* Explorateur générique : découpages non géographiques (milieu social, ...) */}
            <Route path="/explorer/:id" element={<UnitView />} />

            {/* Outils */}
            <Route path="/outils" element={<OutilsList />} />
            <Route path="/outils/representativite" element={<RepresentativiteTool />} />

            {/* Terrains */}
            <Route path="/terrains" element={<TerrainsList />} />
            <Route path="/terrains/elus" element={<TerrainElus />} />
            <Route path="/terrains/ecole" element={<TerrainEcole />} />
            <Route path="/terrains/assemblee" element={<TerrainAssemblee />} />
            <Route path="/terrains/selectivite" element={<TerrainSelectivite />} />
            <Route path="/terrains/auto-ecoles" element={<TerrainAutoEcoles />} />
            <Route path="/terrains/revenus" element={<TerrainRevenus />} />
            <Route path="/terrains/sport" element={<TerrainSport />} />

            {/* Ségrégation résidentielle (revenu + âge, carreaux FiLoSoFi) */}
            <Route path="/segregation" element={<Segregation />} />
            <Route path="/international" element={<International />} />
            <Route path="/international/pisa" element={<Pisa />} />

            {/* Thèmes (dimensions) */}
            <Route path="/themes" element={<ThemesList />} />
            <Route path="/themes/:themeId" element={<ThemeDetail />} />

            {/* Pages statiques */}
            <Route path="/methodologie" element={<Methodologie />} />
            <Route path="/about" element={<About />} />
            <Route path="/mentions-legales" element={<MentionsLegales />} />
            <Route path="/presse" element={<Presse />} />
            <Route path="/newsletter" element={<Newsletter />} />
            <Route path="/fil" element={<Fil />} />

            {/* Toute autre adresse : page introuvable */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </Layout>
  )
}

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <GestionDefilement />
      <Routes>
        {/* Vue intégrable, nue (hors Layout) */}
        <Route
          path="/embed/:type"
          element={
            <ErrorBoundary fallback={<div className="p-6 text-center text-gray-500">Vue indisponible.</div>}>
              <Embed />
            </ErrorBoundary>
          }
        />
        {/* Tout le reste : application normale */}
        <Route path="*" element={<MainApp />} />
      </Routes>
    </Suspense>
  )
}

export default App
