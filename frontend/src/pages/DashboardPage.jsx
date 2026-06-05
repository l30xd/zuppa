import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { ingredientsAPI, recipesAPI } from '../services/api'
import RecipeCard from '../components/RecipeCard'
import styles from './Dashboard.module.css'

export default function DashboardPage() {
  const [ingredients, setIngredients] = useState([])
  const [ingInput, setIngInput] = useState('')
  const [recipes, setRecipes] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingIngs, setLoadingIngs] = useState(true)
  const [error, setError] = useState('')
  const [prefs, setPrefs] = useState({ time: 'media', difficulty: 'media', diet: 'ninguna', count: 2 })

  const fetchIngredients = useCallback(async () => {
    try {
      const { data } = await ingredientsAPI.list()
      setIngredients(data)
    } catch { } finally { setLoadingIngs(false) }
  }, [])

  useEffect(() => { fetchIngredients() }, [fetchIngredients])

  const addIngredients = async () => {
    const parts = ingInput.split(',').map(s => s.trim()).filter(Boolean)
    if (!parts.length) return
    try {
      await ingredientsAPI.addBulk(parts.map(name => ({ name })))
      setIngInput('')
      fetchIngredients()
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al agregar ingrediente.')
    }
  }

  const removeIngredient = async (id) => {
    await ingredientsAPI.remove(id)
    setIngredients(prev => prev.filter(i => i.id !== id))
  }

  const generate = async () => {
    setError('')
    setLoading(true)
    setRecipes([])
    try {
      const { data } = await recipesAPI.generate(prefs)
      setRecipes(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al generar recetas. Revisa tu API key.')
    } finally {
      setLoading(false)
    }
  }

  const toggleFav = async (id, current) => {
    await recipesAPI.toggleFavorite(id, !current)
    setRecipes(prev => prev.map(r => r.id === id ? { ...r, is_favorite: !current } : r))
  }

  return (
    <div className={styles.layout}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.logo}>Zuppa</div>
        <nav className={styles.nav}>
          <span className={styles.navActive}>🌿 Inventario</span>
          <Link to="/history" className={styles.navLink}>📜 Historial</Link>
        </nav>

        <div className={styles.section}>
          <div className={styles.sectionLabel}>Mis ingredientes</div>
          <div className={styles.inputRow}>
            <input
              value={ingInput}
              onChange={e => setIngInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && addIngredients()}
              placeholder="tomate, pollo, arroz…"
              className={styles.ingInput}
            />
            <button className={styles.addBtn} onClick={addIngredients}>+</button>
          </div>

          <div className={styles.tags}>
            {loadingIngs && <span className={styles.hint}>Cargando…</span>}
            {!loadingIngs && ingredients.length === 0 && (
              <span className={styles.hint}>Agrega ingredientes para comenzar</span>
            )}
            {ingredients.map(ing => (
              <span key={ing.id} className={styles.tag}>
                {ing.name}
                <button onClick={() => removeIngredient(ing.id)}>×</button>
              </span>
            ))}
          </div>
        </div>

        <div className={styles.section}>
          <div className={styles.sectionLabel}>Preferencias</div>
          <div className={styles.prefs}>
            {[
              { label: 'Tiempo', key: 'time', options: [['rapida','Rápida (≤20 min)'],['media','Media (≤45 min)'],['elaborada','Elaborada (1h+)']] },
              { label: 'Dificultad', key: 'difficulty', options: [['facil','Fácil'],['media','Media'],['avanzada','Avanzada']] },
              { label: 'Dieta', key: 'diet', options: [['ninguna','Sin restricción'],['vegetariana','Vegetariana'],['vegana','Vegana'],['sin gluten','Sin gluten']] },
              { label: 'Recetas', key: 'count', options: [['1','1 receta'],['2','2 recetas'],['3','3 recetas']] },
            ].map(({ label, key, options }) => (
              <div key={key} className={styles.prefRow}>
                <label>{label}</label>
                <select
                  value={prefs[key]}
                  onChange={e => setPrefs(p => ({ ...p, [key]: key === 'count' ? Number(e.target.value) : e.target.value }))}
                >
                  {options.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                </select>
              </div>
            ))}
          </div>
        </div>

        <button
          className={styles.genBtn}
          onClick={generate}
          disabled={loading || ingredients.length === 0}
        >
          {loading ? 'Generando recetas…' : '✦ Generar recetas'}
        </button>
      </aside>

      {/* Main */}
      <main className={styles.main}>
        {error && <div className={styles.errorBanner}>{error}</div>}

        {!loading && recipes.length === 0 && (
          <div className={styles.welcome}>
            <div className={styles.welcomeIcon}>🌿</div>
            <h2>¿Qué hay en tu cocina?</h2>
            <p>Agrega ingredientes en el panel izquierdo y genera recetas personalizadas con IA.</p>
          </div>
        )}

        {loading && (
          <div className={styles.loadingState}>
            <div className={styles.spinner} />
            <p>Let him cook</p>
          </div>
        )}

        {!loading && recipes.length > 0 && (
          <div className={styles.recipesGrid}>
            {recipes.map(r => (
              <RecipeCard key={r.id} recipe={r} onToggleFav={toggleFav} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
