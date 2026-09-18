import { useCallback, useEffect, useState } from 'react'

/**
 * Small helper hook for calling an async fetcher on mount and exposing
 * { data, loading, error, refetch }. Used by pages that load data from
 * the backend (Dashboard, History) to avoid repeating the same
 * loading/error boilerplate in every component.
 */
export function useAsyncData(fetcher, deps = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    fetcher()
      .then(setData)
      .catch((err) => setError(err?.response?.data?.detail || err.message))
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    load()
  }, [load])

  return { data, loading, error, refetch: load }
}
