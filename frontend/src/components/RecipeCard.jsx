import { useState } from 'react'
import styles from './RecipeCard.module.css'

export default function RecipeCard({ recipe, onToggleFav }) {
  const [open, setOpen] = useState(true)
  const r = recipe.result

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div>
          <h3 className={styles.title}>{r.nombre}</h3>
          {r.descripcion && <p className={styles.desc}>{r.descripcion}</p>}
          <div className={styles.badges}>
            <span className={styles.badgeTime}>⏱ {r.tiempo}</span>
            <span className={styles.badgeDiff}>⚡ {r.dificultad}</span>
            <span className={styles.badgeCal}>🔥 {r.calorias}</span>
            {r.porciones && <span className={styles.badgePor}>👤 {r.porciones} porciones</span>}
          </div>
        </div>
        <div className={styles.actions}>
          <button
            className={`${styles.favBtn} ${recipe.is_favorite ? styles.favActive : ''}`}
            onClick={() => onToggleFav(recipe.id, recipe.is_favorite)}
            title={recipe.is_favorite ? 'Quitar de favoritos' : 'Agregar a favoritos'}
          >
            {recipe.is_favorite ? '★' : '☆'}
          </button>
          <button className={styles.toggleBtn} onClick={() => setOpen(o => !o)}>
            {open ? 'Ocultar ▴' : 'Ver receta ▾'}
          </button>
        </div>
      </div>

      {open && (
        <div className={styles.body}>
          <div className={styles.ingredients}>
            <h4>Ingredientes</h4>
            <ul>
              {(r.ingredientes || []).map((ing, i) => (
                <li key={i} className={ing.esDelInventario ? styles.highlight : ''}>
                  <span className={styles.dot} />
                  <span className={styles.ingName}>{ing.nombre}</span>
                  <span className={styles.ingQty}>{ing.cantidad}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className={styles.steps}>
            <h4>Preparación</h4>
            <ol>
              {(r.pasos || []).map((paso, i) => (
                <li key={i}>
                  <div className={styles.stepNum}>{i + 1}</div>
                  <p>{paso}</p>
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}

      {open && r.consejos && (
        <div className={styles.tip}>
          <strong>💡 Chef dice:</strong> {r.consejos}
        </div>
      )}
    </div>
  )
}
