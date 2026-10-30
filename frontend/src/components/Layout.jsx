import Header from './Header'
import Footer from './Footer'
import BarreOnglets from './BarreOnglets'

function Layout({ children }) {
  return (
    // Sur téléphone, de la place en bas pour la barre d'onglets (et la zone du geste d'accueil).
    <div className="min-h-screen flex flex-col pb-[calc(3.5rem+env(safe-area-inset-bottom))] sm:pb-0">
      <Header />
      <main className="flex-1">
        {children}
      </main>
      <Footer />
      <BarreOnglets />
    </div>
  )
}

export default Layout
