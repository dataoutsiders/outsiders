import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

/**
 * ErrorBoundary - Capture les erreurs React et affiche un fallback
 * 
 * Utilisation :
 * <ErrorBoundary fallback={<p>Erreur de chargement</p>}>
 *   <ComponentQuiPeutPlanter />
 * </ErrorBoundary>
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo })
    // Log l'erreur pour debug
    console.error('ErrorBoundary caught:', error, errorInfo)
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
  }

  render() {
    if (this.state.hasError) {
      // Fallback personnalisé fourni
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Fallback par défaut
      return (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 my-4">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              <AlertTriangle className="w-6 h-6 text-red-500" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-red-800 mb-2">
                Oups, quelque chose s'est mal passé
              </h3>
              <p className="text-red-700 text-sm mb-4">
                {this.props.errorMessage || 
                  'Une erreur est survenue lors du chargement de ce composant.'}
              </p>
              
              {/* Afficher les détails en mode développement */}
              {import.meta.env.DEV && this.state.error && (
                <details className="mb-4">
                  <summary className="text-sm text-red-600 cursor-pointer hover:underline">
                    Détails techniques
                  </summary>
                  <pre className="mt-2 p-3 bg-red-100 rounded text-xs overflow-auto">
                    {this.state.error.toString()}
                    {this.state.errorInfo?.componentStack}
                  </pre>
                </details>
              )}

              <button
                onClick={this.handleRetry}
                className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
              >
                <RefreshCw className="w-4 h-4" />
                Réessayer
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
