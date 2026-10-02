import type { AlignedWord, DiffOp } from '@/types'

import styles from './AlignedWords.module.scss'

const OP_SUBSTITUTE: DiffOp = 'sub'
const OP_DELETE: DiffOp = 'del'
const OP_INSERT: DiffOp = 'ins'

function AlignedToken({ word }: { word: AlignedWord }) {
  if (word.op === OP_SUBSTITUTE) {
    return (
      <>
        <del className={styles['aligned-words__missed']}>{word.expected}</del>
        <ins className={styles['aligned-words__wrong']}>{word.heard}</ins>
      </>
    )
  }
  if (word.op === OP_DELETE) return <del className={styles['aligned-words__missed']}>{word.expected}</del>
  if (word.op === OP_INSERT) return <ins className={styles['aligned-words__wrong']}>{word.heard}</ins>
  return <span className={styles['aligned-words__word']}>{word.heard}</span>
}

interface AlignedWordsProps {
  words: AlignedWord[]
}

export function AlignedWords({ words }: AlignedWordsProps) {
  return (
    <p className={styles['aligned-words']}>
      {words.map((word, index) => (
        <AlignedToken key={String(index)} word={word} />
      ))}
    </p>
  )
}
