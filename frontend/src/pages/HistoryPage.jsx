import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { recipesAPI } from '../services/api'
import RecipeCard from '../components/RecipeCard'
import styles from './Dashboard.module.css'
import hStyles from './History.module.css'

export default function HistoryPage() {
  const [recipes, setRecipes] = useState([])
  const [loading, setLoading] = useState(true)
  const [favOnly, setFavOnly] = useState(false)

  const fetch = async () => {
    setLoading(true)
    try {
      const { data } = await recipesAPI.history({ favorites_only: favOnly })
      setRecipes(data)
    } finally { setLoading(false) }
  }

  useEffect(() => { fetch() }, [favOnly])

  const toggleFav = async (id, current) => {
    await recipesAPI.toggleFavorite(id, !current)
    setRecipes(prev => prev.map(r => r.id === id ? { ...r, is_favorite: !current } : r))
  }

  const deleteEntry = async (id) => {
    await recipesAPI.deleteHistory(id)
    setRecipes(prev => prev.filter(r => r.id !== id))
  }

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>Zuppa</div>
        <nav className={styles.nav}>
          <Link to="/" className={styles.navLink}>🌿 Inventario</Link>
          <span className={styles.navActive}>📜 Historial</span>
        </nav>

        <div className={hStyles.filters}>
          <div className={styles.sectionLabel}>Filtros</div>
          <label className={hStyles.checkLabel}>
            <input type="checkbox" checked={favOnly} onChange={e => setFavOnly(e.target.checked)} />
            Solo favoritos ★
          </label>
        </div>

        <div className={hStyles.stat}>
          <span className={hStyles.statNum}>{recipes.length}</span>
          <span className={hStyles.statLabel}>recetas guardadas</span>
        </div>
      </aside>

      <main className={styles.main}>
        {loading && (
          <div className={styles.loadingState}>
            <div className={styles.spinner} />
          </div>
        )}

        {!loading && recipes.length === 0 && (
          <div className={styles.welcome}>
            <div className={styles.welcomeIcon}>{favOnly ? '★' : '📜'}</div>
            <h2>{favOnly ? 'Sin favoritos aún' : 'Sin historial aún'}</h2>
            <p>Genera recetas desde el inventario y aparecerán aquí automáticamente.</p>
            <Link to="/" style={{ color: 'var(--green-bright)', fontSize: 14, marginTop: '0.5rem' }}>
              → Ir al inventario
            </Link>
          </div>
        )}

        {!loading && recipes.length > 0 && (
          <div className={styles.recipesGrid}>
            {recipes.map(r => (
              <div key={r.id} style={{ position: 'relative' }}>
                <RecipeCard recipe={r} onToggleFav={toggleFav} />
                <button
                  className={hStyles.deleteBtn}
                  onClick={() => deleteEntry(r.id)}
                  title="Eliminar del historial"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
