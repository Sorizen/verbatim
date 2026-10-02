import type { ChangeEvent, SubmitEvent } from 'react'
import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router'

import { MAX_IDEA_LENGTH, MIN_IDEA_LENGTH } from '@/consts'
import { extractQuotedLines, runPath } from '@/helpers'
import { useCreateRun } from '@/hooks'

import styles from './IdeaForm.module.scss'
import { LockedLines } from './LockedLines'

const IDEA_FIELD_ID = 'idea-field'
const IDEA_HINT_ID = 'idea-hint'
const IDEA_ROWS = 7

export function IdeaForm() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const createRun = useCreateRun()
  const [idea, setIdea] = useState('')
  const lockedLines = useMemo(() => extractQuotedLines(idea), [idea])
  const isLongEnough = idea.trim().length >= MIN_IDEA_LENGTH
  const canSubmit = isLongEnough && !createRun.isPending

  function handleChange(event: ChangeEvent<HTMLTextAreaElement>) {
    setIdea(event.target.value)
  }

  function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!canSubmit) return
    createRun.mutate(idea.trim(), {
      onSuccess: (run) => {
        void navigate(runPath(run.id))
      },
    })
  }

  return (
    <form className={styles['idea-form']} onSubmit={handleSubmit}>
      <label htmlFor={IDEA_FIELD_ID} className={styles['idea-form__label']}>
        {t('idea.label')}
      </label>
      <p id={IDEA_HINT_ID} className={styles['idea-form__hint']}>
        {t('idea.hint')}
      </p>
      <textarea
        id={IDEA_FIELD_ID}
        className={styles['idea-form__field']}
        value={idea}
        onChange={handleChange}
        maxLength={MAX_IDEA_LENGTH}
        rows={IDEA_ROWS}
        placeholder={t('idea.placeholder')}
        aria-describedby={IDEA_HINT_ID}
      />
      <LockedLines lines={lockedLines} />
      <div className={styles['idea-form__footer']}>
        <span className={styles['idea-form__counter']}>
          {isLongEnough
            ? t('idea.counter', { count: idea.length, max: MAX_IDEA_LENGTH })
            : t('idea.too-short', { min: MIN_IDEA_LENGTH })}
        </span>
        <button type="submit" className={styles['idea-form__submit']} disabled={!canSubmit}>
          {createRun.isPending ? t('idea.submitting') : t('idea.submit')}
        </button>
      </div>
      {createRun.isError && (
        <p role="alert" className={styles['idea-form__error']}>
          {t('idea.error', { message: createRun.error.message })}
        </p>
      )}
    </form>
  )
}
